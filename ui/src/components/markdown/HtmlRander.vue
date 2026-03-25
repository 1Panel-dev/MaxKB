<template>
  <iframe
    ref="htmlRef"
    class="iframe"
    style="border: 0; width: 100%"
    :srcdoc="fSource"
    sandbox="allow-scripts"
  />
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount, inject } from 'vue'
const chatUserProfile = inject('chatUserProfile') as any
const htmlRef = ref<HTMLIFrameElement>()
const props = withDefaults(
  defineProps<{
    source?: string
    script_exec?: boolean
    sendMessage?: (question: string, type: 'old' | 'new', other_params_data?: any) => void
  }>(),
  {
    source: '',
    script_exec: true,
  },
)

// 每个实例生成唯一 id，防止多个 iframe 消息串扰
const instanceId = Math.random().toString(36).slice(2)

function createIframeHtml(sourceHtml: string) {
  return `
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { margin: 0 !important; padding: 0 !important; overflow: hidden; }
</style>
<script>
const _INSTANCE_ID = '${instanceId}';
window.chatUserProfile=function chatUserProfile() {
  return new Promise((resolve, reject) => {
    const requestId = Date.now() + '_' + Math.random()

    function handler(e) {
      const data = e.data

      if (
        data?.type === 'chatUserProfile:response' &&
        data.requestId === requestId
      ) {
        window.removeEventListener('message', handler)
        resolve(data.data)
      }
    }
    window.addEventListener('message', handler)
    parent.postMessage(
      {
        type: 'chatUserProfile',
        requestId,
        instanceId: _INSTANCE_ID
      },
      '*'
    )

    setTimeout(() => {
      window.removeEventListener('message', handler)
      reject(new Error('timeout'))
    }, 10000)
  })
}
<\/script>
</head>
<body>
${sourceHtml}
<script>
const INSTANCE_ID = '${instanceId}';

function sendMessage(message) {
  parent.postMessage({ type: 'chatMessage', instanceId: INSTANCE_ID, message }, '*');
}
let lastSentHeight = 0;
let timer = null;

function sendHeight() {
  const height = Math.max(
    document.body.scrollHeight,
    document.body.offsetHeight,
    document.documentElement.offsetHeight
  );
  if (height === lastSentHeight) return;
  lastSentHeight = height;
  parent.postMessage({ type: 'resize', instanceId: INSTANCE_ID, height }, '*');
}

window.onload = sendHeight;

const observer = new ResizeObserver(() => {
  clearTimeout(timer);
  timer = setTimeout(sendHeight, 100);
});
observer.observe(document.body);
<\/script>
</body>
</html>
`
}

const fSource = computed(() => createIframeHtml(props.source))

function onMessage(e: MessageEvent) {
  if (e.data?.instanceId !== instanceId) return

  if (e.data.type === 'resize') {
    const iframe = htmlRef.value
    if (!iframe) return
    iframe.style.height = e.data.height + 'px'
  }

  if (e.data.type === 'chatMessage') {
    props.sendMessage?.(e.data.message, 'new')
  }
  if (e.data?.type === 'chatUserProfile') {
    const iframe = htmlRef.value
    if (!iframe) return
    chatUserProfile().then((ok: any) => {
      iframe.contentWindow?.postMessage(
        {
          type: 'chatUserProfile:response',
          requestId: e.data.requestId,
          data: ok,
        },
        '*',
      )
    })
  }
}

onMounted(() => {
  window.addEventListener('message', onMessage)
})

onBeforeUnmount(() => {
  window.removeEventListener('message', onMessage)
})
</script>
