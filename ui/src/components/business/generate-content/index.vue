<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, useTemplateRef, watch } from 'vue'
import type { ScrollbarInstance } from 'element-plus'
import type { PromptGenerateMessage } from '@/api/types'
import { ConversationStream } from '@/conversation-panel/core/stream'
import { inputShortcut } from '@/conversation-panel/core/shortcuts'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'GenerateContent' })

const props = withDefaults(
  defineProps<{
    title: string
    placeholder: string
    emptyText: string
    disabled?: boolean
    request: (messages: PromptGenerateMessage[]) => Promise<Response>
  }>(),
  { disabled: false },
)
const emit = defineEmits<{
  open: []
  closed: []
  replace: [content: string]
}>()
defineSlots<{
  'header-extra'(props: { loading: boolean }): unknown
}>()

// 生成会话：业务方提供请求上下文，组件统一维护输入、消息和弹窗。
const visible = ref(false)
const loading = ref(false)
const inputValue = ref('')
const messages = ref<PromptGenerateMessage[]>([])
const scrollbarRef = useTemplateRef<ScrollbarInstance>('scrollbarRef')
const latestAnswer = computed(() => [...messages.value].reverse().find(({ role }) => role === 'ai')?.content ?? '')
let conversationStream: ConversationStream | undefined

function open() {
  if (props.disabled) return
  emit('open')
  visible.value = true
}

function resetData() {
  stopGenerate()
  loading.value = false
  inputValue.value = ''
  messages.value = []
  emit('closed')
}

// 流式生成：重新生成追加用户消息，停止后保留已生成的内容。
function generateContent(regenerate = false) {
  const content = inputValue.value.trim()
  if (loading.value || props.disabled || (!regenerate && !content)) return
  messages.value.push({ content: regenerate ? 'Re generate' : content, role: 'user' })
  const requestMessages = [...messages.value]
  inputValue.value = ''
  loading.value = true
  const answer = reactive<PromptGenerateMessage>({ content: '', role: 'ai' })
  messages.value.push(answer)

  function complete(error?: unknown) {
    if (error) {
      messages.value = messages.value.filter((message) => message !== answer)
      if (!(error instanceof Error) || error.name !== 'StreamRequestError') {
        MsgError(error instanceof Error ? error.message : '生成失败')
      }
    }
    conversationStream = undefined
    loading.value = false
  }

  return props
    .request(requestMessages)
    .then((response) => {
      conversationStream = new ConversationStream(
        response,
        (chunk: { content?: string; error?: string }) => {
          if (chunk.error) {
            stopGenerate()
            complete(new Error(chunk.error))
            return
          }
          answer.content += chunk.content ?? ''
          nextTick(() => scrollbarRef.value?.setScrollTop(Number.MAX_SAFE_INTEGER))
        },
        complete,
      )
      return conversationStream.start()
    })
    .catch(complete)
}

function stopGenerate() {
  if (conversationStream) {
    conversationStream.cancel()
    loading.value = false
    conversationStream = undefined
  }
}

function replaceContent() {
  if (!latestAnswer.value || loading.value) return
  emit('replace', latestAnswer.value)
  visible.value = false
}

// 需求输入：回车发送，组合键在光标处换行，输入法确认时不提交。
function handleKeydown(event: KeyboardEvent) {
  inputShortcut(event, inputValue, () => generateContent())
}

// 关闭或卸载时停止读取，关闭动画结束后清理会话。
watch(visible, (value) => {
  if (!value) stopGenerate()
})
onBeforeUnmount(stopGenerate)
</script>

<template>
  <!-- 打开内容生成弹窗 -->
  <el-button text type="primary" :disabled="disabled" @click="open">
    <MkIcon name="icon_star" />
  </el-button>
  <MkDialog v-model="visible" :title="title" @closed="resetData">
    <template v-if="$slots['header-extra']" #header="{ titleId }">
      <div class="flex-between mr-4 -mt-[2px]">
        <h4 :id="titleId">{{ title }}</h4>
        <slot name="header-extra" :loading="loading" />
      </div>
    </template>

    <div class="space-y-4 rounded-xl bg-N100 p-4">
      <el-scrollbar v-if="latestAnswer" ref="scrollbarRef" max-height="320">
        <div class="whitespace-pre-wrap break-words">{{ latestAnswer }}</div>
      </el-scrollbar>
      <div v-else-if="loading" class="flex-align-center gap-2">
        <LoadingIcon :size="16" />
        <span class="mk-dotting">生成中</span>
      </div>
      <p v-else class="flex-align-center gap-2">
        <MkIcon name="icon_star" class="text-primary!" />
        <span>{{ emptyText }}</span>
      </p>
      <div v-if="!loading && latestAnswer">
        <!-- 替换当前内容 -->
        <el-button type="primary" @click="replaceContent">替换</el-button>
        <!-- 重新生成内容 -->
        <el-button plain :disabled="disabled" @click="generateContent(true)">重新生成</el-button>
      </div>
      <div class="mk-input-box border transition-colors hover:border-primary focus-within:border-primary">
        <el-input
          v-model="inputValue"
          type="textarea"
          resize="none"
          :autosize="{ minRows: 1, maxRows: 10 }"
          :placeholder="placeholder"
          :maxlength="100000"
          @keydown.stop="handleKeydown"
          @paste.stop
        />
        <div class="text-right">
          <!-- 停止生成内容 -->
          <el-button v-if="loading" circle type="primary" @click="stopGenerate">
            <MkIcon name="icon_square_filled" />
          </el-button>
          <!-- 发送需求并生成内容 -->
          <el-button v-else circle type="primary" :disabled="!inputValue.trim() || disabled" @click="generateContent()">
            <MkIcon name="icon_arrow-up_outlined" />
          </el-button>
        </div>
      </div>
    </div>
  </MkDialog>
</template>
