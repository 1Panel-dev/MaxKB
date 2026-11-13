<script setup lang="ts">
import { computed, inject, nextTick, onBeforeUnmount, ref, useTemplateRef ,provide} from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import type LogicFlow from '@logicflow/core'
import type { ScrollbarInstance } from 'element-plus'
import type { DefaultModelSettingPayload, ModelItem, ModelProviderItem } from '@/api/types'
import SelectModel from '@/components/business/select-model/index.vue'
import ContentList from '@/conversation-panel/components/content-list/index.vue'
import QuickQuestion from '@/conversation-panel/components/markdown-renderer/QuickQuestion.vue'
import { Scroll } from '@/conversation-panel/core/scroll'
import { inputShortcut } from '@/conversation-panel/core/shortcuts'
import { MsgError, MsgSuccess } from '@/utils/message'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import { useAgent } from '../impl'
import { layoutCanvas } from '../tools/canvas'
import { clearDebugLog, resumeMessages } from '../common'
import { createAgent } from '../create-agent'
import type { AgentEvent, AgentHandle, AgentMessage } from '../type'
import { createActivity } from './activity'
import { VIEW_KEY,VIEW_TYPE } from '@/conversation-panel/view'
provide(VIEW_KEY,VIEW_TYPE.DEBUG)
defineOptions({ name: 'WorkflowAiGeneratePanel' })
const props = withDefaults(
  defineProps<{
    getLogicFlow: () => LogicFlow | undefined
    defaultModelSettings?: DefaultModelSettingPayload
    workflowMode?: WorkflowMode
  }>(),
  { defaultModelSettings: undefined, workflowMode: WorkflowMode.Application },
)
const emit = defineEmits<{ (event: 'done'): void }>()

const resourceScope = inject('resourceScope', 'workspace')
const route = useRoute()
const store = useWorkflowStore(resourceScope)

type GenerateStatus = 'idle' | 'running' | 'done' | 'error' | 'stopped'

const visible = ref(false)
const status = ref<GenerateStatus>('idle')
const requirement = ref('')
const modelId = ref('')
const modelParams = ref<Record<string, unknown>>({})
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const scrollbarRef = useTemplateRef<ScrollbarInstance>('scrollbarRef')
const activity = createActivity()
const busy = computed(() => status.value === 'running')
const started = computed(() => status.value !== 'idle')

const suggestedRequirements = [
  '做一个产品客服，先查产品知识库回答，查不到时礼貌兜底。',
  '做一个可以查询产品收费信息的智能体。',
  '做一个需要时可以转人工服务的客服智能体。',
]

function sendSuggestedRequirement(question: string) {
  if (!modelId.value || busy.value) return
  requirement.value = question
  submit()
}

let agent: AgentHandle | null = null
/** 停止后保留的历史，重建 agent 时续上（已 abort 的 agent 不可复用） */
let carriedMessages: AgentMessage[] | undefined
/** 本次会话的首条需求：停止后重建 agent 时仍作为整体目标背景，不被续聊文字覆盖 */
let sessionGoal: string | undefined

function loadModels() {
  Promise.all([store.getModelListWithShared({ model_type: 'LLM' }), store.getProviderList()])
    .then(([models, providers]) => {
      providerOptions.value = providers
      modelOptions.value = models
      if (!modelId.value) {
        const defaultModelId = props.defaultModelSettings?.LLM?.model_id
        modelId.value = models.find((model) => model.id === defaultModelId)?.id ?? models[0]?.id ?? ''
        modelParams.value = modelId.value === defaultModelId ? cloneDeep(props.defaultModelSettings?.LLM?.model_params_setting ?? {}) : {}
      }
    })
    .catch(() => MsgError('获取模型列表失败'))
}

function open() {
  visible.value = true
  if (!modelOptions.value.length) loadModels()
}

function close() {
  if (busy.value) return
  visible.value = false
}

/* 底部跟随与对话面板共用 Scroll：用户上滑查看时停止跟随，回到底部附近恢复。 */
let bottomScroll: Scroll | undefined
let bottomScrollElement: HTMLElement | undefined
let followPending = false

/** 抽屉内容可能重新挂载，滚动容器变化时重建跟随实例 */
function getBottomScroll() {
  const wrap = scrollbarRef.value?.wrapRef
  if (!wrap) return undefined
  if (wrap !== bottomScrollElement) {
    bottomScroll?.destroy()
    bottomScroll = new Scroll(wrap)
    bottomScrollElement = wrap
  }
  return bottomScroll
}

/** 流式增量：仅在用户停留在底部附近时跟随；同一轮渲染内的多次增量只滚动一次 */
function followBottom() {
  if (followPending) return
  followPending = true
  nextTick(() => {
    followPending = false
    getBottomScroll()?.scrollBottom()
  })
}

/** 用户发送需求：回到最新内容并恢复跟随 */
function forceBottom() {
  nextTick(() => getBottomScroll()?.forceBottom())
}

/** 会改动画布的顶层工具；本轮未调用时视为仅规划 / 答复（如等待用户确认方案），不提示生成完成 */
const CANVAS_MUTATING_TOOLS = new Set(['add_node', 'add_edge', 'delete_node', 'delete_edge', 'configure_node', 'layout'])
let canvasChanged = false

/** 顶层 agent 的总结已作为正文流入活动，失败作为 FAILURE 项展示 */
function onEvent(event: AgentEvent) {
  if (event.type === 'tool_start' && !event.position.length && CANVAS_MUTATING_TOOLS.has(event.name)) canvasChanged = true
  activity.pushEvent(event)
  followBottom()
}

/** 画布所属资源 id：按模式取路由上的应用 / 工具 / 知识库 id */
function resourceIdOf(): string | undefined {
  const key = props.workflowMode.startsWith('knowledge')
    ? 'knowledgeId'
    : props.workflowMode.startsWith('tool')
      ? 'toolId'
      : 'applicationId'
  return typeof route.params[key] === 'string' ? (route.params[key] as string) : undefined
}

/** 首轮装配父 agent，后续续聊复用同一实例以保留上下文 */
async function run(text: string) {
  const lf = props.getLogicFlow()
  if (!lf) return
  if (!agent) {
    sessionGoal ??= text
    agent = createAgent(
      useAgent(props.workflowMode, {
        rootLf: lf,
        modelId: modelId.value,
        modelParams: cloneDeep(modelParams.value),
        call: { onNext: onEvent },
        workflowMode: props.workflowMode,
        resourceScope,
        resourceId: resourceIdOf(),
        position: [],
        maxIterations: 200,
        context: sessionGoal,
        messages: carriedMessages,
      }),
    )
    carriedMessages = undefined
  }
  status.value = 'running'
  canvasChanged = false
  const current = agent
  const result = await current.run(text)
  // 运行期间已新建会话：结果作废，不回写状态
  if (agent !== current) return
  if (result.status === 'done') {
    status.value = 'done'
    if (!canvasChanged) return
    await layoutCanvas(lf)
    lf.fitView()
    MsgSuccess('工作流已生成，请检查后保存')
    emit('done')
  } else if (result.status === 'error') {
    status.value = 'error'
  } else {
    status.value = 'stopped'
    // 已 abort 的 agent 不能复用：保留可续聊的历史，丢弃实例，下次发送时重建续聊
    carriedMessages = resumeMessages(current.messages)
    agent = null
  }
}

function submit() {
  const text = requirement.value.trim()
  if (!text || !modelId.value || busy.value) return
  requirement.value = ''
  if (status.value === 'idle') {
    clearDebugLog()
    activity.reset()
  }
  activity.pushQuestion(text)
  forceBottom()
  run(text)
}

function stop() {
  agent?.stop()
}

/** 新建会话：丢弃上下文与活动记录，画布保持现状 */
function reset() {
  agent?.stop()
  agent = null
  carriedMessages = undefined
  sessionGoal = undefined
  activity.reset()
  status.value = 'idle'
}

function handleKeydown(event: KeyboardEvent) {
  inputShortcut(event, requirement, submit)
}

onBeforeUnmount(() => {
  agent?.stop()
  bottomScroll?.destroy()
})

defineExpose({ open, close })
</script>

<template>
  <MkDrawer
    v-model="visible"
    title="AI 生成"
    size="480"
    class="top-header! h-layout-content! max-w-full rounded-tl-xl!"
    content-class="h-full p-0!"
    :modal="false"
    modal-penetrable
    :lock-scroll="false"
  >
    <template #header>
      <div class="flex-between flex-1">
        <h4 class="flex-align-center gap-2">
          <MkIcon name="icon_star_colorful" />
          AI 生成
        </h4>
        <!-- 新建生成会话 -->
        <el-button text :disabled="busy || !started" @click="reset" class="mr-2">
          <MkIcon name="icon_new-chat_outlined" size="18" />
        </el-button>
      </div>
    </template>
    <div class="flex h-full flex-col" @keydown.stop @paste.stop>
      <el-scrollbar ref="scrollbarRef" class="min-h-0 flex-1 p-4">
        <div class="space-y-3">
          <div v-if="!started">
            <p>请描述你的需求，如下</p>
            <div class="flex flex-col items-start">
              <template v-for="question in suggestedRequirements" :key="question">
                <!-- 发送示例需求生成工作流 -->
                <QuickQuestion class="ml-0!" :question="question" :send-message="sendSuggestedRequirement" />
              </template>
            </div>
          </div>
          <ContentList v-else :content-list="activity.activityItems.value" />
          <div v-if="busy" class="flex-align-center gap-2 text-N600">
            <span class="mk-dotting">{{ activity.lastActivity.value || '生成中' }}</span>
          </div>
          <p v-if="status === 'stopped'" class="text-N500">已停止生成</p>
        </div>
      </el-scrollbar>

      <div class="mk-input-box m-4 mt-0 border shadow-lg transition-colors focus-within:border-primary/60">
        <el-input
          v-model="requirement"
          type="textarea"
          resize="none"
          :autosize="{ minRows: 1, maxRows: 7 }"
          placeholder="请描述你的需求"
          :maxlength="10000"
          @keydown="handleKeydown"
        />
        <div class="mt-4 flex-between">
          <SelectModel
            class="w-50!"
            v-model="modelId"
            v-model:model-params="modelParams"
            can-edit-params
            :can-add="false"
            :options="modelOptions"
            :provider-options="providerOptions"
            :disabled="started"
            placeholder="请选择模型"
            teleported
          />
          <div>
            <!-- 停止生成 -->
            <el-button v-if="busy" circle type="primary" @click="stop">
              <MkIcon name="icon_square_filled" />
            </el-button>
            <!-- 发送需求开始生成 -->
            <el-button v-else circle type="primary" :disabled="!requirement.trim() || !modelId" @click="submit">
              <MkIcon name="icon_arrow-up_outlined" />
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </MkDrawer>
</template>
