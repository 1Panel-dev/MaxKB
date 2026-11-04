<script setup lang="ts">
import { computed, useId, type Component } from 'vue'
import type { Dict } from '@/api/types'
import loadErrorImage from '@/assets/conversation/load_error.png'
import { useSendQuestionOptional } from '../message-input/index'
import { parseRenderNodes, type RenderTag } from './parse-tags'
import QuickQuestion from './QuickQuestion.vue'
import IframeRender from './IframeRender.vue'
import FormRender from './FormRender.vue'
import ReasoningRender from './ReasoningRender.vue'
import ToolCallsRender from './tool-calls-render/index.vue'
import HtmlItem from '../content/items/html.vue'
import EchartsItem from '../content/items/echarts.vue'

defineOptions({ name: 'MarkdownRenderer' })

const props = withDefaults(
  defineProps<{
    source?: string
    reasoning_content?: string
  }>(),
  { source: '', reasoning_content: '' },
)

const editorIdPrefix = `markdown-renderer-${useId()}`
const renderNodes = computed(() => parseRenderNodes(props.source))

// 日志等只读视图拿不到发送能力，标签内的发送入口随之禁用
const sendMessage = useSendQuestionOptional() ?? undefined

interface TagRenderer {
  component: Component
  props: (content: string) => Dict<unknown>
}

const tagRenderers: Record<RenderTag, TagRenderer> = {
  quick_question: { component: QuickQuestion, props: (question) => ({ question, sendMessage }) },
  // HTML、图表标签与同类型内容项共用渲染
  html_rander: { component: HtmlItem, props: (source) => ({ content: { content: source } }) },
  iframe_render: { component: IframeRender, props: (source) => ({ source, sendMessage }) },
  echarts_rander: { component: EchartsItem, props: (option) => ({ content: { content: option } }) },
  tool_calls_render: { component: ToolCallsRender, props: (content) => ({ content }) },
  form_rander: { component: FormRender, props: (formSetting) => ({ formSetting }) },
}

// 回答中的外部链接在新窗口打开；页内锚点（脚注等）保持默认
function openLinkInNewTab(event: MouseEvent) {
  const link = (event.target as HTMLElement | null)?.closest('a[href]')
  if (!(link instanceof HTMLAnchorElement) || link.getAttribute('href')?.startsWith('#')) return
  if (!['http:', 'https:'].includes(link.protocol)) return
  link.target = '_blank'
  link.rel = 'noopener noreferrer'
}

// 图片加载失败时替换为占位图，只替换一次避免占位图也失败时循环
function replaceBrokenImage(event: Event) {
  const image = event.target
  if (!(image instanceof HTMLImageElement) || image.dataset.loadError) return
  image.dataset.loadError = 'true'
  image.src = loadErrorImage
}
</script>

<template>
  <div @click="openLinkInNewTab" @error.capture="replaceBrokenImage">
    <ReasoningRender v-if="reasoning_content.trim()" :content="reasoning_content" />

    <template v-for="(node, index) in renderNodes" :key="index">
      <MdPreview v-if="node.type === 'markdown'" :editor-id="`${editorIdPrefix}-${index}`" :model-value="node.content" />
      <component :is="tagRenderers[node.type].component" v-else v-bind="tagRenderers[node.type].props(node.content)" />
    </template>
  </div>
</template>
