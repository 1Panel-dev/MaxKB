<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Loading, Top } from '@element-plus/icons-vue'
import type { ScrollbarInstance } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import SelectModel from '@/components/business/select-model/index.vue'
import type { ModelItem, ModelProviderItem, PromptGenerateMessage, PromptGeneratePayload } from '@/api/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'AiChatNodePromptGenerate' })

const props = defineProps<{
  modelId: string
  disabled: boolean
  modelOptions: ModelItem[]
  providerOptions: ModelProviderItem[]
}>()
const emit = defineEmits<{ replace: [prompt: string] }>()
const route = useRoute()

const PROMPT_TEMPLATE = `请根据用户描述生成一个完整的 AI 角色人设模板：

用户需求：{userInput}

请直接输出最终角色设定，不要输出解释、前言或额外说明。角色设定需要包含角色、目标、核心技能、工作流、输出格式和限制，并始终服务于用户描述的核心功能。`

const visible = ref(false)
const loading = ref(false)
const inputValue = ref('')

const applicationId = ref('')
const activeModelId = ref('')
const messages = ref<PromptGenerateMessage[]>([])
const scrollbarRef = useTemplateRef<ScrollbarInstance>('scrollbarRef')
let abortController: AbortController | undefined

const lastRequestMessages = ref<PromptGenerateMessage[]>([])

const latestAnswer = computed(() => [...messages.value].reverse().find(({ role }) => role === 'ai')?.content ?? '')

function resetData() {
  abortController?.abort()
  abortController = undefined
  applicationId.value = ''
  inputValue.value = ''
  loading.value = false
  messages.value = []
  lastRequestMessages.value = []
  activeModelId.value = ''
}

// 生成入口：打开时初始化本次使用的智能体和模型，关闭后清理会话。
function open() {
  if (props.disabled) return
  resetData()
  applicationId.value = typeof route.params.applicationId === 'string' ? route.params.applicationId : ''
  activeModelId.value = props.modelId
  visible.value = true
}

function scrollToBottom() {
  nextTick(() => scrollbarRef.value?.setScrollTop(Number.MAX_SAFE_INTEGER))
}

function appendStreamEvent(eventText: string, answer: PromptGenerateMessage) {
  const data = eventText
    .split(/\r?\n/)
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())
    .join('\n')
  if (!data || data === '[DONE]') return

  const chunk = JSON.parse(data) as { content?: string; error?: string }
  if (chunk.error) throw new Error(chunk.error)
  answer.content += chunk.content ?? ''
  scrollToBottom()
}

async function readStream(response: Response, answer: PromptGenerateMessage, signal: AbortSignal) {
  if (!response.body) throw new Error('生成接口未返回可读取的数据流')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    buffer += decoder.decode(value, { stream: !done })
    const events = buffer.split(/\r?\n\r?\n/)
    buffer = events.pop() ?? ''
    if (signal.aborted) return
    events.forEach((eventText) => appendStreamEvent(eventText, answer))
    if (done) break
  }
  if (buffer.trim()) appendStreamEvent(buffer, answer)
}

// 生成和重试共享请求流程，重试复用上次请求，避免重复追加用户消息。
async function generate(regenerate = false) {
  const content = inputValue.value.trim()
  if (loading.value || !applicationId.value || !activeModelId.value) return
  if (regenerate ? !lastRequestMessages.value.length : !content) return

  const requestMessages: PromptGenerateMessage[] = regenerate
    ? lastRequestMessages.value.map((message) => ({ ...message }))
    : [...messages.value.map((message) => ({ ...message })), { content, role: 'user' }]
  lastRequestMessages.value = requestMessages
  const answer = reactive<PromptGenerateMessage>({ content: '', role: 'ai' })
  messages.value = [...requestMessages, answer]
  if (!regenerate) inputValue.value = ''
  loading.value = true
  const controller = new AbortController()
  abortController = controller

  const payload: PromptGeneratePayload = { messages: requestMessages, prompt: PROMPT_TEMPLATE }
  try {
    const response = await ApplicationApi.postPromptGenerate(applicationId.value, activeModelId.value, payload, controller.signal)
    if (controller.signal.aborted) return
    await readStream(response, answer, controller.signal)
  } catch (error) {
    if (controller.signal.aborted) return
    messages.value = messages.value.filter((message) => message !== answer)
    if (!(error instanceof Error) || error.name !== 'StreamRequestError') {
      MsgError(error instanceof Error ? error.message : '提示词生成失败')
    }
  } finally {
    if (abortController === controller) {
      loading.value = false
      abortController = undefined
    }
  }
}

// 主题输入：回车发送，Shift+Enter 换行，中文输入法确认时不提交。
function handleInputKeydown(event: KeyboardEvent) {
  if (event.isComposing || event.key !== 'Enter' || event.shiftKey) return
  event.preventDefault()
  generate()
}

function stopGenerate() {
  abortController?.abort()
}

watch(visible, (value) => {
  if (!value) stopGenerate()
})

function replacePrompt() {
  if (!latestAnswer.value || loading.value) return
  emit('replace', latestAnswer.value)
  visible.value = false
}

onBeforeUnmount(() => abortController?.abort())
</script>

<template>
  <el-button text type="primary" :disabled="disabled" @click="open">
    <MkIcon name="icon_star" />
  </el-button>
  <MkDialog v-model="visible" title="生成提示词" width="720" @closed="resetData">
    <template #header="{ titleId, titleClass }">
      <div class="flex-align-center justify-between gap-4 pr-10">
        <span :id="titleId" :class="titleClass" class="shrink-0">生成提示词</span>
        <div class="min-w-0 w-70">
          <SelectModel v-model="activeModelId" :options="modelOptions" :provider-options="providerOptions" :disabled="loading" teleported />
        </div>
        <el-divider direction="vertical" />
      </div>
    </template>

    <div class="space-y-4 rounded-xl bg-N100 p-4">
      <div v-if="loading" class="flex-align-center gap-2">
        <MkIcon :icon="Loading" class="animate-spin text-primary" />
        <span>生成中</span>
      </div>
      <el-scrollbar v-if="latestAnswer" ref="scrollbarRef" max-height="320">
        <div class="whitespace-pre-wrap break-words">{{ latestAnswer }}</div>
      </el-scrollbar>
      <div v-if="!loading && lastRequestMessages.length" class="flex gap-3">
        <el-button type="primary" :disabled="!latestAnswer" @click="replacePrompt">替换</el-button>
        <el-button class="ml-0!" :disabled="!activeModelId" @click="generate(true)">重新生成</el-button>
      </div>

      <div class="prompt-input overflow-hidden rounded-xl border bg-white transition-colors hover:border-primary focus-within:border-primary">
        <el-input
          v-model="inputValue"
          type="textarea"
          resize="none"
          :autosize="{ minRows: 1, maxRows: 10 }"
          placeholder="请输入提示词主题"
          :maxlength="100000"
          @keydown="handleInputKeydown"
        />
        <div class="flex justify-end px-2 pb-2 pt-1">
          <!-- 停止生成提示词 -->
          <el-button v-if="loading" class="input-action" circle size="small" type="primary" @click="stopGenerate">
            <MkIcon name="icon_stop_filled" />
          </el-button>
          <!-- 发送主题并生成提示词 -->
          <el-button
            v-else
            class="input-action"
            circle
            size="small"
            type="primary"
            :disabled="!inputValue.trim() || !activeModelId || !applicationId"
            @click="generate()"
          >
            <MkIcon :icon="Top" :size="16" />
          </el-button>
        </div>
      </div>
    </div>
  </MkDialog>
</template>

<style scoped lang="scss">
/* 提示词主题输入与操作栏 */
.prompt-input {
  :deep(.el-textarea__inner) {
    background: transparent;
    border-radius: 0;
    box-shadow: none;
    padding: calc(var(--spacing) * 2) calc(var(--spacing) * 2) 0;
  }

  .input-action {
    min-height: 0;
    padding: 0;

    &.is-disabled {
      background-color: var(--mk-N400);
      border-color: var(--mk-N400);
    }
  }
}
</style>
