<script setup lang="ts">
import { computed, inject, nextTick, onBeforeUnmount, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { ScrollbarInstance } from 'element-plus'
import type { DefaultModelSettingPayload, ModelItem } from '@/api/types'
import ContentList from '@/conversation-panel/components/content-list/index.vue'
import { inputShortcut } from '@/conversation-panel/core/shortcuts'
import { MsgError, MsgSuccess } from '@/utils/message'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import { useApplicationAgent } from '../application'
import { layoutCanvas } from '../tools/canvas'
import { clearDebugLog } from '../common'
import { createAgent } from '../create-agent'
import type { AgentEvent, AgentHandle } from '../type'
import { createActivity } from './activity'

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
const modelOptions = ref<ModelItem[]>([])
const scrollbarRef = useTemplateRef<ScrollbarInstance>('scrollbarRef')
const activity = createActivity()
const busy = computed(() => status.value === 'running')
const started = computed(() => status.value !== 'idle')

let agent: AgentHandle | null = null

function loadModels() {
  store
    .getModelListWithShared({ model_type: 'LLM' })
    .then((models) => {
      modelOptions.value = models
      if (!modelId.value) {
        const defaultModelId = props.defaultModelSettings?.LLM?.model_id
        modelId.value = models.find((model) => model.id === defaultModelId)?.id ?? models[0]?.id ?? ''
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

function scrollToBottom() {
  nextTick(() => scrollbarRef.value?.setScrollTop(Number.MAX_SAFE_INTEGER))
}

/** 顶层 agent 的总结已作为正文流入活动，失败作为 FAILURE 项展示 */
function onEvent(event: AgentEvent) {
  activity.pushEvent(event)
  scrollToBottom()
}

/** 首轮装配父 agent，后续续聊复用同一实例以保留上下文 */
async function run(text: string) {
  const lf = props.getLogicFlow()
  if (!lf) return
  if (!agent) {
    agent = createAgent(
      useApplicationAgent({
        rootLf: lf,
        modelId: modelId.value,
        call: { onNext: onEvent },
        workflowMode: props.workflowMode,
        resourceScope,
        resourceId: typeof route.params.applicationId === 'string' ? route.params.applicationId : undefined,
        position: [],
        maxIterations: 200,
        context: text,
      }),
    )
  }
  status.value = 'running'
  const result = await agent.run(text)
  if (result.status === 'done') {
    status.value = 'done'
    await layoutCanvas(lf)
    lf.fitView()
    MsgSuccess('工作流已生成，请检查后保存')
    emit('done')
  } else if (result.status === 'error') {
    status.value = 'error'
  } else {
    status.value = 'stopped'
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
  scrollToBottom()
  run(text)
}

function stop() {
  agent?.stop()
}

/** 新建会话：丢弃上下文与活动记录，画布保持现状 */
function reset() {
  agent?.stop()
  agent = null
  activity.reset()
  status.value = 'idle'
}

function handleKeydown(event: KeyboardEvent) {
  inputShortcut(event, requirement, submit)
}

onBeforeUnmount(() => agent?.stop())

defineExpose({ open, close })
</script>

<template>
  <div
    v-if="visible"
    class="absolute top-4 right-4 bottom-4 z-20 flex w-105 flex-col rounded-xl border border-N300 bg-white shadow-lg"
    @keydown.stop
    @paste.stop
  >
    <div class="flex-between shrink-0 border-b border-N300 px-4 py-3">
      <h4 class="flex-align-center gap-2">
        <MkIcon name="icon_star" class="text-primary!" />
        AI 生成工作流
      </h4>
      <div class="flex-align-center gap-1">
        <!-- 新建生成会话 -->
        <el-button text :disabled="busy || !started" @click="reset">
          <MkIcon name="icon_new-chat_outlined" />
        </el-button>
        <!-- 关闭生成面板 -->
        <el-button text :disabled="busy" @click="close">
          <MkIcon name="icon_close_outlined" />
        </el-button>
      </div>
    </div>

    <el-scrollbar ref="scrollbarRef" class="min-h-0 flex-1">
      <div class="space-y-3 p-4">
        <p v-if="!started" class="mk-gray-card text-N600">
          描述你想要的智能体，例如：“做一个产品客服，先查产品知识库回答，查不到时礼貌兜底”。AI
          会规划流程、添加节点、连线并完成配置，生成后请检查再保存。
        </p>
        <ContentList v-else :content-list="activity.activityItems.value" />
        <div v-if="busy" class="flex-align-center gap-2 text-N600">
          <LoadingIcon :size="16" />
          <span class="mk-dotting">{{ activity.lastActivity.value || '生成中' }}</span>
        </div>
        <p v-if="status === 'stopped'" class="text-N500">已停止生成</p>
      </div>
    </el-scrollbar>

    <div class="shrink-0 space-y-2 border-t border-N300 p-4">
      <el-select v-model="modelId" :disabled="started" placeholder="选择生成用的模型" filterable class="w-full" :teleported="false">
        <el-option v-for="model in modelOptions" :key="model.id" :label="model.name" :value="model.id" />
      </el-select>
      <div class="mk-input-box border transition-colors hover:border-primary focus-within:border-primary">
        <el-input
          v-model="requirement"
          type="textarea"
          resize="none"
          :autosize="{ minRows: 2, maxRows: 8 }"
          :placeholder="started ? '继续描述要调整的地方' : '描述你想要的智能体工作流'"
          :maxlength="10000"
          @keydown="handleKeydown"
        />
        <div class="mt-2 text-right">
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
</template>
