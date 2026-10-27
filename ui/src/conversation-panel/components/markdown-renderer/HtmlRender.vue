<script setup lang="ts">
import { computed, inject, ref } from 'vue'
import { useIframeBridge, type IframeSendMessage } from './iframe-bridge'

defineOptions({ name: 'MarkdownHtmlRender' })

const props = withDefaults(defineProps<{ source?: string; sendMessage?: IframeSendMessage }>(), { source: '' })

// v3 视图未 provide 时返回 null，iframe 内 chatUserProfile() 拿到空值
const getChatUserProfile = inject<() => Promise<unknown>>('chatUserProfile', () => Promise.resolve(null))

const iframeRef = ref<HTMLIFrameElement>()
const { buildSrcdoc } = useIframeBridge(iframeRef, {
  extended: true,
  sendMessage: (question, otherParams) => props.sendMessage?.(question, otherParams),
  getChatUserProfile,
})
const srcdoc = computed(() => buildSrcdoc(props.source))
</script>

<template>
  <iframe ref="iframeRef" class="w-full border-0" :srcdoc="srcdoc" allow="geolocation" sandbox="allow-scripts" />
</template>
