<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, useTemplateRef } from 'vue'
import { MagicStick, Promotion } from '@element-plus/icons-vue'
import type { ScrollbarInstance } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type { PromptGenerateMessage, PromptGeneratePayload } from '@/api/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'AiChatNodePromptGenerateDialog' })

const emit = defineEmits<{ replace: [prompt: string] }>()

const PROMPT_TEMPLATE = `请根据用户描述生成一个完整的 AI 角色人设模板：

用户需求：{userInput}

请直接输出最终角色设定，不要输出解释、前言或额外说明。角色设定需要包含角色、目标、核心技能、工作流、输出格式和限制，并始终服务于用户描述的核心功能。`

const visible = ref(false)
const loading = ref(false)
const inputValue = ref('')
const applicationId = ref('')
const modelId = ref('')
const messages = ref<PromptGenerateMessage[]>([])
const scrollbarRef = useTemplateRef<ScrollbarInstance>('scrollbarRef')
let abortController: AbortController | undefined

const latestAnswer = computed(() => [...messages.value].reverse().find(({ role }) => role === 'ai')?.content ?? '')

function resetData() {
  abortController?.abort()
  abortController = undefined
  applicationId.value = ''
  inputValue.value = ''
  loading.value = false
  messages.value = []
  modelId.value = ''
}

function open(currentApplicationId: string, currentModelId: string) {
  resetData()
  applicationId.value = currentApplicationId
  modelId.value = currentModelId
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

async function readStream(response: Response, answer: PromptGenerateMessage) {
  if (!response.body) throw new Error('生成接口未返回可读取的数据流')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    buffer += decoder.decode(value, { stream: !done })
    const events = buffer.split(/\r?\n\r?\n/)
    buffer = events.pop() ?? ''
    events.forEach((eventText) => appendStreamEvent(eventText, answer))
    if (done) break
  }
  if (buffer.trim()) appendStreamEvent(buffer, answer)
}

async function generate() {
  const content = inputValue.value.trim()
  if (!content || loading.value || !applicationId.value || !modelId.value) return

  const userMessage: PromptGenerateMessage = { content, role: 'user' }
  const answer = reactive<PromptGenerateMessage>({ content: '', role: 'ai' })
  messages.value.push(userMessage, answer)
  inputValue.value = ''
  loading.value = true
  const controller = new AbortController()
  abortController = controller

  const payload: PromptGeneratePayload = { messages: messages.value.slice(0, -1), prompt: PROMPT_TEMPLATE }
  try {
    const response = await ApplicationApi.postPromptGenerate(applicationId.value, modelId.value, payload, controller.signal)
    await readStream(response, answer)
  } catch (error) {
    if (controller.signal.aborted) return
    messages.value = messages.value.filter((message) => message !== answer)
    if (!(error instanceof Error) || error.name !== 'StreamRequestError') {
      MsgError(error instanceof Error ? error.message : '提示词生成失败')
    }
  } finally {
    loading.value = false
    if (abortController === controller) abortController = undefined
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key !== 'Enter' || event.shiftKey) return
  event.preventDefault()
  void generate()
}

function replacePrompt() {
  if (!latestAnswer.value) return
  emit('replace', latestAnswer.value)
  visible.value = false
}

onBeforeUnmount(() => abortController?.abort())
defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="AI 生成系统提示词" width="720" @closed="resetData">
    <div class="flex h-120 flex-col gap-3">
      <el-scrollbar ref="scrollbarRef" class="min-h-0 flex-1 rounded-md border border-N200 bg-N50 p-3">
        <div v-if="messages.length" class="flex flex-col gap-3 pr-2">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="message.role === 'user' ? 'ml-16 bg-primary-50' : 'mr-16 bg-white'"
            class="rounded-md border border-N200 p-3 whitespace-pre-wrap"
          >
            <div class="mb-1 text-sm text-N600">{{ message.role === 'user' ? '你的需求' : '生成结果' }}</div>
            <span v-if="message.content">{{ message.content }}</span>
            <span v-else class="mk-dotting text-N600">生成中</span>
          </div>
        </div>
        <div v-else class="flex h-full flex-col items-center justify-center gap-2 py-20 text-N600">
          <MkIcon :icon="MagicStick" class="text-primary" />
          <span>描述智能体的角色、目标和工作内容，AI 将生成完整系统提示词</span>
        </div>
      </el-scrollbar>

      <div class="flex items-end gap-2">
        <el-input
          v-model="inputValue"
          :autosize="{ minRows: 2, maxRows: 6 }"
          maxlength="100000"
          placeholder="例如：创建一个产品售后客服，负责排查问题并给出处理步骤"
          type="textarea"
          @keydown="handleKeydown"
        />
        <el-button circle :disabled="!inputValue.trim() || loading" type="primary" @click="generate">
          <MkIcon :icon="Promotion" />
        </el-button>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button :disabled="!latestAnswer || loading" type="primary" @click="replacePrompt">替换系统提示词</el-button>
    </template>
  </MkDialog>
</template>
