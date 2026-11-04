<script setup lang="ts">
import { computed, ref } from 'vue'
import { useIframeBridge } from '../../markdown-renderer/iframe-bridge'
import { useSendQuestionOptional } from '../../message-input/index'
import { useChatUserProfileGetter } from '../../../view/index'

defineOptions({ name: 'ContentHtmlItem' })

const props = defineProps<{
  content: { content?: string | null }
}>()

// 日志等只读视图拿不到发送能力，iframe 内 sendMessage 随之失效
const sendQuestion = useSendQuestionOptional()
// 仅 Chat 入口提供，Admin 调试、日志中 iframe 内 chatUserProfile() 拿到 null
const getChatUserProfile = useChatUserProfileGetter()

// 回复 HTML 在沙箱 iframe 中渲染，脚本与父页面隔离
const iframeRef = ref<HTMLIFrameElement>()
const { buildSrcdoc } = useIframeBridge(iframeRef, {
  extended: true,
  sendMessage: (question, otherParams) => sendQuestion?.(question, otherParams),
  getChatUserProfile,
})
const srcdoc = computed(() => buildSrcdoc(props.content.content ?? ''))
</script>

<template>
  <iframe ref="iframeRef" class="w-full border-0" :srcdoc="srcdoc" allow="geolocation" sandbox="allow-scripts" />
</template>
