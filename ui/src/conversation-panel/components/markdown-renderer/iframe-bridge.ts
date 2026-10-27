/** html_rander / iframe_render 共用的沙箱 iframe：生成 srcdoc，并处理 iframe 发回的高度、发送消息、跳转与用户信息请求。 */

import { onBeforeUnmount, onMounted, type Ref } from 'vue'
import type { Dict } from '@/api/types'
import { randomId } from '@/utils/common'

export type IframeSendMessage = (question: string, otherParams?: Dict<unknown>) => void

interface IframeBridgeOptions {
  /** 是否向 iframe 暴露 jump、chatUserProfile。 */
  extended: boolean
  sendMessage?: IframeSendMessage
  getChatUserProfile?: () => Promise<unknown>
}

// 跳转、获取用户信息仅 html_rander 提供
const EXTENDED_SCRIPT = `
window.jump = function jump(url) {
  parent.postMessage({ type: 'jump', instanceId: INSTANCE_ID, url }, '*');
};
window.chatUserProfile = function chatUserProfile() {
  return new Promise((resolve, reject) => {
    const requestId = Date.now() + '_' + Math.random();
    function handler(e) {
      if (e.data?.type === 'chatUserProfile:response' && e.data.requestId === requestId) {
        window.removeEventListener('message', handler);
        resolve(e.data.data);
      }
    }
    window.addEventListener('message', handler);
    parent.postMessage({ type: 'chatUserProfile', requestId, instanceId: INSTANCE_ID }, '*');
    setTimeout(() => {
      window.removeEventListener('message', handler);
      reject(new Error('timeout'));
    }, 10000);
  });
};`

// 高度上报、发送消息，以及导出 PDF/图片时由 iframe 自身序列化 DOM（父页面无法读取沙箱内容）
const BODY_SCRIPT = `
function sendMessage(message, other_params_data) {
  parent.postMessage({ type: 'chatMessage', instanceId: INSTANCE_ID, message, other_params_data }, '*');
}
let lastSentHeight = 0;
let timer = null;
function sendHeight() {
  const height = Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.offsetHeight);
  if (height === lastSentHeight) return;
  lastSentHeight = height;
  parent.postMessage({ type: 'resize', instanceId: INSTANCE_ID, height }, '*');
}
window.onload = sendHeight;
new ResizeObserver(() => {
  clearTimeout(timer);
  timer = setTimeout(sendHeight, 100);
}).observe(document.body);
window.addEventListener('message', function (e) {
  if (e.source !== parent || e.data?.type !== 'snapshot') return;
  let html = '';
  try {
    const doc = document.documentElement.cloneNode(true);
    const srcCanvas = document.querySelectorAll('canvas');
    doc.querySelectorAll('canvas').forEach(function (c, i) {
      try {
        const img = document.createElement('img');
        img.src = srcCanvas[i].toDataURL();
        img.style.cssText = srcCanvas[i].style.cssText;
        img.style.width = srcCanvas[i].offsetWidth + 'px';
        img.style.height = srcCanvas[i].offsetHeight + 'px';
        c.replaceWith(img);
      } catch (err) {}
    });
    doc.querySelectorAll('script').forEach(function (s) { s.remove(); });
    html = '<!DOCTYPE html>' + doc.outerHTML;
  } catch (err) {}
  parent.postMessage({ type: 'snapshot:response', requestId: e.data.requestId, html: html }, '*');
});`

function createIframeHtml(sourceHtml: string, instanceId: string, extended: boolean) {
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { margin: 0 !important; padding: 0 !important; overflow: hidden; }
</style>
<script>
const INSTANCE_ID = '${instanceId}';${extended ? EXTENDED_SCRIPT : ''}
<\/script>
</head>
<body>
${sourceHtml}
<script>${BODY_SCRIPT}
<\/script>
</body>
</html>`
}

/** 只放行 http(s) 地址，避免 javascript: 等协议在新窗口中以当前站点身份执行。 */
function openExternalUrl(url: unknown) {
  if (typeof url !== 'string') return
  try {
    const target = new URL(url, window.location.href)
    if (['http:', 'https:'].includes(target.protocol)) window.open(target.href, '_blank', 'noopener,noreferrer')
  } catch {
    // 非法地址直接忽略
  }
}

export function useIframeBridge(iframeRef: Ref<HTMLIFrameElement | undefined>, options: IframeBridgeOptions) {
  // 每个实例生成唯一 id，防止多个 iframe 消息串扰
  const instanceId = randomId()

  function onMessage(event: MessageEvent) {
    const iframe = iframeRef.value
    // 同时校验来源窗口与实例 id，忽略其他页面或其他 iframe 伪造的消息
    if (!iframe || event.source !== iframe.contentWindow || event.data?.instanceId !== instanceId) return

    switch (event.data.type) {
      case 'resize':
        iframe.style.height = `${event.data.height}px`
        break
      case 'chatMessage':
        options.sendMessage?.(event.data.message, event.data.other_params_data)
        break
      case 'jump':
        if (options.extended) openExternalUrl(event.data.url)
        break
      case 'chatUserProfile':
        if (!options.extended || !options.getChatUserProfile) break
        options.getChatUserProfile().then((profile) => {
          iframe.contentWindow?.postMessage({ type: 'chatUserProfile:response', requestId: event.data.requestId, data: profile }, '*')
        })
        break
    }
  }

  onMounted(() => window.addEventListener('message', onMessage))
  onBeforeUnmount(() => window.removeEventListener('message', onMessage))

  return { buildSrcdoc: (sourceHtml: string) => createIframeHtml(sourceHtml, instanceId, options.extended) }
}
