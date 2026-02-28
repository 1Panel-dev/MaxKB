<template>
  <div class="iframe-wrapper">
    <iframe
      v-show="visible"
      ref="iframeRef"
      class="iframe"
      :srcdoc="finalSource"
      @load="resize"
      sandbox="allow-scripts allow-same-origin"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
const resize = async () => {
  await nextTick()

  const iframe = iframeRef.value
  if (!iframe) return

  const doc = iframe.contentDocument
  if (!doc) return

  const contentHeight = doc.documentElement.scrollHeight || doc.body.scrollHeight

  const viewportHeight = window.innerHeight

  const finalHeight = Math.min(contentHeight, viewportHeight)

  iframe.style.height = finalHeight + 'px'

  iframe.style.overflow = contentHeight > viewportHeight ? 'auto' : 'hidden'
}
const props = withDefaults(
  defineProps<{
    source?: string
    script_exec?: boolean
    visible?: boolean
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
  if (props.script_exec) return props.source

  return props.source.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
})

// 如果 source 改变才刷新 iframe
watch(
  () => props.source,
  () => {
    if (iframeRef.value) {
      iframeRef.value.srcdoc = finalSource.value
    }
  },
)
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
