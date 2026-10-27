<script setup lang="ts">
import { computed, ref } from 'vue'
import { useIframeBridge, type IframeSendMessage } from './iframe-bridge'

defineOptions({ name: 'MarkdownIframeRender' })

const props = withDefaults(defineProps<{ source?: string; sendMessage?: IframeSendMessage }>(), { source: '' })

const iframeRef = ref<HTMLIFrameElement>()
// iframe_render 只上报高度和发送消息，不提供跳转与用户信息
const { buildSrcdoc } = useIframeBridge(iframeRef, {
  extended: false,
  sendMessage: (question) => props.sendMessage?.(question),
})
const srcdoc = computed(() => buildSrcdoc(props.source))
</script>

<template>
  <iframe ref="iframeRef" class="w-full border-0" :srcdoc="srcdoc" allow="geolocation" sandbox="allow-scripts" />
</template>
