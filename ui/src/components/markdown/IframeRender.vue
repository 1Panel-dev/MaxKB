<template>
  <div class="iframe-wrapper">
    <iframe
      v-show="visible"
      ref="iframeRef"
      style="border: 0; width: 100%"
      class="iframe"
      :srcdoc="finalSource"
      sandbox="allow-scripts"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
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

const props = withDefaults(
  defineProps<{
    source?: string
    script_exec?: boolean
    visible?: boolean
    sendMessage?: (question: string, type: 'old' | 'new', other_params_data?: any) => void
  }>(),
  {
    source: '',
    script_exec: true,
    visible: true,
  },
)

const iframeRef = ref<HTMLIFrameElement>()

// 如果不允许执行 script，就过滤掉
const finalSource = computed(() => {
  if (props.script_exec) return fSource.value

  return fSource.value.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
})
function onMessage(e: MessageEvent) {
  if (e.data?.instanceId !== instanceId) return

  if (e.data.type === 'resize') {
    const iframe = iframeRef.value
    if (!iframe) return
    iframe.style.height = e.data.height + 'px'
  }

  if (e.data.type === 'chatMessage') {
    props.sendMessage?.(e.data.message, 'new')
  }
}

onMounted(() => {
  window.addEventListener('message', onMessage)
})
onBeforeUnmount(() => {
  window.removeEventListener('message', onMessage)
})
</script>

<style scoped>
.iframe-wrapper {
  width: 100%;
  height: 100%;
}
.iframe {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
