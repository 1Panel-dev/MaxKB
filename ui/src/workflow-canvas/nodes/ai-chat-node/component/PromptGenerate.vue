<script setup lang="ts">
import { computed, nextTick, reactive, ref, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Top, Loading } from '@element-plus/icons-vue'
import type { ScrollbarInstance } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type { ModelItem, ModelProviderItem, PromptGenerateMessage, PromptGeneratePayload } from '@/api/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'AiChatNodePromptGenerate' })

const props = defineProps<{
  modelId: string
  disabled: boolean
  modelOptions?: ModelItem[]
  providerOptions: ModelProviderItem[]
}>()
const emit = defineEmits<{ replace: [prompt: string] }>()
const route = useRoute()

// 提示词模板：约束生成结果的角色结构与内容范围。
const PROMPT_TEMPLATE = `请根据用户描述生成一个完整的AI角色人设模板:

用户需求：{userInput}

重要说明：
1. 角色设定必须服务于"{userInput}"内容设定应用的核心功能
2. 允许用户对角色设定的具体内容进行调整和优化
3. 如果用户要求修改某个技能或部分，在保持应用主题的前提下进行相应调整

请按以下格式生成：

必须严格遵循以下规则：
1. **严格禁止输出解释、前言、额外说明**，只输出最终结果。
2. **严格使用以下格式**，不能缺少标题、不能多出其他段落。
3. **如果用户要求修改角色设定的某个部分，在保持应用核心功能的前提下进行调整**。
4. **如果用户需求与角色设定生成完全无关（如闲聊、其他话题），则主要依据应用信息生成标准角色设定，但不完全忽略用户输入，可从中提取有价值的辅助信息（如领域背景、语气风格等）作为次要参考**。

# 角色:
角色概述和主要职责的一句话描述

## 目标：
角色的工作目标,如果有多目标可以分点列出,但建议更聚焦1-2个目标

## 核心技能：
### 技能 1: [技能名称，如作品推荐/信息查询/专业分析等]
1. [执行步骤1 - 描述该技能的第一个具体操作步骤，包括条件判断和处理方式]
2. [执行步骤2 - 描述该技能的第二个具体操作步骤，包括如何获取或处理信息]
3. [执行步骤3 - 描述该技能的最终输出步骤，说明如何呈现结果]

===回复示例===
- 📋 [标识符]: <具体内容格式说明>
- 🎯 [标识符]: <具体内容格式说明>
- 💡 [标识符]: <具体内容格式说明>
===示例结束===

### 技能 2: [技能名称]
1. [执行步骤1 - 描述触发条件和初始处理方式]
2. [执行步骤2 - 描述信息获取和深化处理的具体方法]
3. [执行步骤3 - 描述最终输出的具体要求和格式]

### 技能 3: [技能名称]
- [核心能力描述 - 说明该技能的主要作用和知识基础]
- [应用方法 - 描述如何运用该技能为用户提供服务，包括具体的实施方式]

## 工作流：
1. 描述角色工作流程的第一步
2. 描述角色工作流程的第二步
3. 描述角色工作流程的第三步

## 输出格式：
如果对角色的输出格式有特定要求，可以在这里强调并举例说明想要的输出格式


## 限制：
1. **严格限制回答范围**：仅回答与角色设定相关的问题。
   - 如果用户提问与角色无关，必须使用以下固定格式回复：
     “对不起，我只能回答与[角色设定]相关的问题，您的问题不在服务范围内。”
   - 不得提供任何与角色设定无关的回答。
2. 描述角色在互动过程中需要遵循的限制条件2
3. 描述角色在互动过程中需要遵循的限制条件3

输出时不得包含任何解释或附加说明，只能返回符合以上格式的内容。`

// 生成会话：维护弹窗、模型、输入和本次请求上下文。
const visible = ref(false)
const loading = ref(false)
const inputValue = ref('')
const applicationId = ref('')
const activeModelId = ref('')
const messages = ref<PromptGenerateMessage[]>([])
const lastRequestMessages = ref<PromptGenerateMessage[]>([])
const scrollbarRef = useTemplateRef<ScrollbarInstance>('scrollbarRef')

const latestAnswer = computed(() => [...messages.value].reverse().find(({ role }) => role === 'ai')?.content ?? '')

// 弹窗生命周期
/** 清理生成会话，供打开弹窗和关闭动画结束时复用。 */
function resetData() {
  applicationId.value = ''
  inputValue.value = ''
  loading.value = false
  messages.value = []
  lastRequestMessages.value = []
  activeModelId.value = ''
}

/** 初始化当前智能体与模型，并打开生成弹窗。 */
function open() {
  if (props.disabled) return
  resetData()
  applicationId.value = route.params.applicationId as string
  activeModelId.value = props.modelId
  visible.value = true
}

// 流式结果处理
/** 等待结果渲染后滚动到底部，持续展示最新生成内容。 */
function scrollToBottom() {
  nextTick(() => scrollbarRef.value?.setScrollTop(Number.MAX_SAFE_INTEGER))
}

/** 解析单个 SSE 事件，追加文本并将服务端错误交给请求流程处理。 */
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

/** 按事件边界读取响应流，保留跨数据块的未完整事件。 */
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

// 生成操作
/** 提交输入并读取生成结果；重试时复用上次请求，避免重复追加用户消息。 */
async function generatePrompt(regenerate = false) {
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

  const payload: PromptGeneratePayload = { messages: requestMessages, prompt: PROMPT_TEMPLATE }
  try {
    const response = await ApplicationApi.postPromptGenerate(applicationId.value, activeModelId.value, payload)
    await readStream(response, answer)
  } catch (error) {
    messages.value = messages.value.filter((message) => message !== answer)
    if (!(error instanceof Error) || error.name !== 'StreamRequestError') {
      MsgError(error instanceof Error ? error.message : '提示词生成失败')
    }
  } finally {
    loading.value = false
  }
}

/** 停止生成的预留入口，当前尚未接入请求取消逻辑。 */
function stopGenerate() {}

/** Enter 提交主题，Shift+Enter 和输入法组合输入保留原生行为。 */
function handleKeydown(event: KeyboardEvent) {
  if (event.isComposing || event.key !== 'Enter' || event.shiftKey) return
  event.preventDefault()
  void generatePrompt()
}

/** 将最新生成结果交给父节点替换系统提示词，并关闭弹窗。 */
function replacePrompt() {
  if (!latestAnswer.value || loading.value) return
  emit('replace', latestAnswer.value)
  visible.value = false
}

/** 重新生成按钮的预留入口，当前尚未调用重试流程。 */
function handleReGenerate() {}

// 弹窗关闭时调用停止入口，会话数据在关闭动画结束后统一清理。
watch(visible, (value) => {
  if (!value) stopGenerate()
})
</script>

<template>
  <!-- 生成入口：打开系统提示词生成弹窗。 -->
  <el-button text type="primary" :disabled="disabled" @click="open">
    <MkIcon name="icon_star" />
  </el-button>
  <MkDialog v-model="visible" title="生成提示词" @closed="resetData">
    <div class="flex flex-col gap-4 rounded-xl bg-N100 p-4">
      <div v-if="loading" class="flex items-center gap-2">
        <MkIcon :icon="Loading" class="animate-spin text-primary" />
        <span>生成中</span>
      </div>
      <el-scrollbar v-if="latestAnswer" ref="scrollbarRef" max-height="320">
        <div class="whitespace-pre-wrap break-words">{{ latestAnswer }}</div>
      </el-scrollbar>
      <div v-if="!loading && lastRequestMessages.length" class="flex gap-3">
        <!-- 替换：将最新结果回写到节点的系统提示词。 -->
        <el-button type="primary" :disabled="!latestAnswer" @click="replacePrompt">替换</el-button>
        <!-- 重新生成：预留按钮，重试逻辑待接入。 -->
        <el-button class="ml-0!" :disabled="!activeModelId" @click="handleReGenerate">重新生成</el-button>
      </div>

      <div class="prompt-generate-input relative overflow-hidden rounded-2xl bg-white">
        <el-input
          v-model="inputValue"
          :autosize="{ minRows: 3, maxRows: 6 }"
          maxlength="100000"
          placeholder="请输入提示词主题"
          type="textarea"
          resize="none"
          @keydown="handleKeydown"
        />
        <!-- 停止生成：生成期间显示，请求取消逻辑待接入。 -->
        <el-button v-if="loading" class="absolute right-3 bottom-3" circle type="primary" @click="stopGenerate">
          <span class="h-3 w-3 rounded-sm bg-white" />
        </el-button>
        <!-- 发送：提交输入主题；缺少主题、模型或智能体时禁用。 -->
        <el-button
          v-else
          class="absolute right-3 bottom-3"
          circle
          type="primary"
          :disabled="!inputValue.trim() || !activeModelId || !applicationId"
          @click="generatePrompt()"
        >
          <MkIcon :icon="Top" />
        </el-button>
      </div>
    </div>
  </MkDialog>
</template>

<style scoped lang="scss"></style>
