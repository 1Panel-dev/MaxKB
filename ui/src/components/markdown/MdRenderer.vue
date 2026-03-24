<template>
  <div>
    <!-- 推理过程 -->
    <ReasoningRander v-if="reasoning_content?.trim()" :content="reasoning_content" />

    <template v-for="(item, index) in mdViewList" :key="index">
      <!-- 动态组件 -->
      <component
        v-if="componentMap[item.type]"
        :is="componentMap[item.type]"
        v-bind="getComponentProps(item)"
      />

      <!-- 快捷问题 -->
      <div
        v-else-if="item.type === 'question'"
        class="problem-button mt-4 mb-4"
        :class="sendMessage && type !== 'log' ? 'cursor' : 'disabled'"
        @click="handleQuestionClick(item.content)"
      >
        <el-space :size="8" alignment="flex-start">
          <AppIcon iconName="app-edit" class="color-primary" style="margin-top: 3px" />
          {{ item.content }}
        </el-space>
      </div>

      <!-- Markdown -->
      <MdPreview v-else editorId="preview-only" :modelValue="item.content" class="maxkb-md" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { config } from 'md-editor-v3'
import HtmlRander from './HtmlRander.vue'
import EchartsRander from './EchartsRander.vue'
import FormRander from './FormRander.vue'
import ReasoningRander from './ReasoningRander.vue'
import IframeRender from './IframeRender.vue'
import ToolCallsRender from './tool-calls-render/index.vue'
config({
  markdownItConfig(md) {
    md.renderer.rules.image = (tokens, idx, options) => {
      tokens[idx].attrSet('style', 'display:inline-block;min-height:33px;padding:0;margin:0')
      tokens[idx].attrSet('onerror', 'this.src="/load_error.png"')
      return md.renderer.renderToken(tokens, idx, options)
    }

    md.renderer.rules.link_open = (tokens, idx, options) => {
      tokens[idx].attrSet('target', '_blank')
      return md.renderer.renderToken(tokens, idx, options)
    }
  },
})

const props = withDefaults(
  defineProps<{
    source?: string
    reasoning_content?: string
    sendMessage?: (question: string, type: 'old' | 'new', other_params_data?: any) => void
    child_node?: any
    chat_record_id?: string
    runtime_node_id?: string
    disabled?: boolean
    type?: 'log' | 'ai-chat' | 'debug-ai-chat' | 'share'
  }>(),
  {
    source: '',
    disabled: false,
  },
)

type RenderNode = {
  type: string
  content: string
}

interface TagPlugin {
  tag: string
  type: string
  nested?: boolean
  transform?: (content: string) => any
}

const TAG_PLUGINS: TagPlugin[] = [
  { tag: 'quick_question', type: 'question' },
  { tag: 'html_rander', type: 'html_rander' },
  { tag: 'iframe_render', type: 'iframe_render' },
  { tag: 'tool_calls_render', type: 'tool_calls_render' },
  {
    tag: 'echarts_rander',
    type: 'echarts_rander',
    transform: (c) => {
      return c
    },
  },
  { tag: 'form_rander', type: 'form_rander', nested: true },
]

function parseByPlugin(source: string, plugin: TagPlugin): RenderNode[] {
  const startTag = `<${plugin.tag}>`
  const endTag = `</${plugin.tag}>`

  if (!source.includes(startTag)) {
    return [{ type: 'md', content: source }]
  }

  const result: RenderNode[] = []
  let cursor = 0

  while (cursor < source.length) {
    const start = source.indexOf(startTag, cursor)

    if (start === -1) {
      result.push({
        type: 'md',
        content: source.slice(cursor),
      })
      break
    }

    if (start > cursor) {
      result.push({
        type: 'md',
        content: source.slice(cursor, start),
      })
    }

    let end = source.indexOf(endTag, start)
    if (end === -1) break

    // 处理嵌套
    if (plugin.nested) {
      let depth = 1
      let tempIndex = start + startTag.length

      while (depth > 0) {
        const nextStart = source.indexOf(startTag, tempIndex)
        const nextEnd = source.indexOf(endTag, tempIndex)

        if (nextStart !== -1 && nextStart < nextEnd) {
          depth++
          tempIndex = nextStart + startTag.length
        } else {
          depth--
          tempIndex = nextEnd + endTag.length
          end = nextEnd
        }
      }
    }

    let content = source.slice(start + startTag.length, end)

    if (plugin.transform) {
      content = plugin.transform(content)
    }

    result.push({
      type: plugin.type,
      content,
    })

    cursor = end + endTag.length
  }

  return result
}

function parseContent(source: string): RenderNode[] {
  let nodes: RenderNode[] = [{ type: 'md', content: source }]

  TAG_PLUGINS.forEach((plugin) => {
    nodes = nodes.flatMap((node) => {
      if (node.type !== 'md') return node
      return parseByPlugin(node.content, plugin)
    })
  })

  return nodes
}

const mdViewList = computed(() => {
  return parseContent(props.source || '')
})

const componentMap: Record<string, any> = {
  html_rander: HtmlRander,
  echarts_rander: EchartsRander,
  form_rander: FormRander,
  iframe_render: IframeRender,
  tool_calls_render: ToolCallsRender,
}

function getComponentProps(item: RenderNode) {
  switch (item.type) {
    case 'form_rander':
      return {
        chat_record_id: props.chat_record_id,
        runtime_node_id: props.runtime_node_id,
        child_node: props.child_node,
        disabled: props.disabled,
        sendMessage: props.sendMessage,
        form_setting: item.content,
      }

    case 'echarts_rander':
      return { option: item.content }
    case 'html_rander':
      return { source: item.content, sendMessage: props.sendMessage }
    case 'iframe_render':
      return { source: item.content, sendMessage: props.sendMessage }
    case 'tool_calls_render':
      return { content: item.content }

    default:
      return {}
  }
}

function handleQuestionClick(content: string) {
  if (!props.sendMessage) return
  if (props.type === 'log') return
  props.sendMessage(content, 'new')
}
</script>

<style scoped lang="scss">
.problem-button {
  width: 100%;
  border-radius: 8px;
  background: var(--app-layout-bg-color);
  padding: 12px;
  box-sizing: border-box;
  word-break: break-all;

  &:hover {
    background: var(--el-color-primary-light-9);
  }

  &.disabled:hover {
    background: var(--app-layout-bg-color);
  }
}
</style>
