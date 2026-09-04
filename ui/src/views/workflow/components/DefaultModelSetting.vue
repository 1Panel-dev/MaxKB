<script setup lang="ts">
import { computed, onBeforeUnmount, provide, ref, watch } from 'vue'
import { ClickOutside as vClickOutside } from 'element-plus'
import { cloneDeep, isEqual } from 'lodash'
import type LogicFlow from '@logicflow/core'
import type ModelApi from '@/api/admin/workspace/model/model'
import ModelProviderApi from '@/api/admin/model-provider'
import type { Dict, ModelItem, ModelProviderItem } from '@/api/types'
import ModelSelect from '@/components/business/model-select/index.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import type WorkflowCanvas from '@/workflow-canvas/index.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'DefaultModelSetting' })

const defaultModelTypes = [
  { type: 'LLM', label: '大语言模型' },
  { type: 'TTS', label: '语音合成模型' },
  { type: 'STT', label: '语音识别模型' },
  { type: 'IMAGE', label: '图片理解模型' },
  { type: 'TTI', label: '图片生成模型' },
  { type: 'TTV', label: '文本生成视频模型' },
  { type: 'ITV', label: '图片生成视频模型' },
  { type: 'RERANKER', label: '重排序模型' },
] as const

type DefaultModelType = (typeof defaultModelTypes)[number]['type']
interface ModelSetting {
  model_id?: string
  model_params_setting?: Dict<unknown>
}
type DefaultModelSettings = Partial<Record<DefaultModelType, ModelSetting>>
type ModelSourceField =
  | 'model_id_type'
  | 'stt_model_id_type'
  | 'tts_model_id_type'
  | 'reranker_model_id_type'
  | 'long_term_model_id_type'
  | 'tts_type'
interface ModelNodeData extends Partial<Record<ModelSourceField, string>> {
  stt_model_enable?: boolean
  tts_model_enable?: boolean
  long_term_enable?: boolean
  loop_body?: LogicFlow.GraphConfigData
}

const props = withDefaults(
  defineProps<{
    modelValue?: DefaultModelSettings
    modelApi: typeof ModelApi
    modelQuery?: Dict<unknown>
    show?: boolean
    workflowRef?: InstanceType<typeof WorkflowCanvas> | null
    readonly?: boolean
  }>(),
  { modelValue: () => ({}), modelQuery: () => ({}), show: false, workflowRef: null, readonly: false },
)
const emit = defineEmits<{
  'update:modelValue': [settings: DefaultModelSettings]
  save: []
  close: []
}>()

// 暂存模型设置：编辑和参数弹窗只修改副本，保存时才通知页面提交。
function normalizeSettings(settings: DefaultModelSettings) {
  return Object.fromEntries(
    defaultModelTypes.map(({ type }) => [
      type,
      {
        ...cloneDeep(settings[type]),
        model_id: settings[type]?.model_id || '',
        model_params_setting: cloneDeep(settings[type]?.model_params_setting || {}),
      },
    ]),
  ) as Record<DefaultModelType, ModelSetting & { model_id: string; model_params_setting: Dict<unknown> }>
}

const modelSettings = ref(normalizeSettings(props.modelValue))
const hasChanges = computed(() => !props.readonly && !isEqual(modelSettings.value, normalizeSettings(props.modelValue)))

function resetSettings() {
  modelSettings.value = normalizeSettings(props.modelValue)
}

function handleModelChange(modelType: DefaultModelType) {
  modelSettings.value[modelType].model_params_setting = {}
}

function handleSave() {
  if (props.readonly || !hasChanges.value) return
  emit('update:modelValue', cloneDeep(modelSettings.value))
  emit('save')
}

// 模型资源：调用方选择当前范围的完整 API，组件不通过 URL 推断资源范围。
const modelOptions = ref<Partial<Record<DefaultModelType, ModelItem[]>>>({})
const providerOptions = ref<ModelProviderItem[]>([])
const loading = ref(false)
let loadSequence = 0

provide('getModelParamsForm', (modelId: string) => props.modelApi.getModelParamsForm(modelId))

function loadModelOptions() {
  const sequence = ++loadSequence
  loading.value = true
  modelOptions.value = {}
  providerOptions.value = []
  const providerRequest = ModelProviderApi.getProviderList().then((providers) => {
    if (sequence === loadSequence) providerOptions.value = providers
  })
  const modelRequests = defaultModelTypes.map(({ type }) =>
    props.modelApi.getModelList({ ...props.modelQuery, model_type: type }).then((models) => {
      if (sequence === loadSequence) modelOptions.value[type] = models
    }),
  )
  // 请求层统一提示失败；单个类别失败不阻断其他类别展示。
  return Promise.allSettled([providerRequest, ...modelRequests]).finally(() => {
    if (sequence === loadSequence) loading.value = false
  })
}

watch(
  () => props.show,
  (visible) => {
    if (!visible) {
      loadSequence += 1
      return
    }
    resetSettings()
    loadModelOptions()
  },
  { immediate: true },
)
onBeforeUnmount(() => {
  loadSequence += 1
})

// 应用默认来源：保留自定义模型配置，并递归处理循环体中的节点。
const applying = ref(false)

function applyDefaultSources(graph: LogicFlow.GraphData) {
  let changedCount = 0
  const pendingNodes: LogicFlow.NodeConfig[] = [...graph.nodes]
  const updateSource = (nodeData: ModelNodeData, field: ModelSourceField, source = 'default') => {
    if (nodeData[field] === source) return
    nodeData[field] = source
    changedCount += 1
  }

  while (pendingNodes.length) {
    const node = pendingNodes.pop()!
    const nodeData = node.properties?.node_data as ModelNodeData | undefined
    if (!nodeData) continue

    if (node.type === WorkflowNodeType.Base) {
      if (nodeData.stt_model_enable) updateSource(nodeData, 'stt_model_id_type')
      if (nodeData.tts_model_enable && nodeData.tts_type !== 'BROWSER') updateSource(nodeData, 'tts_type', 'DEFAULT')
      if (nodeData.long_term_enable) updateSource(nodeData, 'long_term_model_id_type')
      continue
    }

    if (node.type === WorkflowNodeType.SpeechToTextNode) updateSource(nodeData, 'stt_model_id_type')
    else if (node.type === WorkflowNodeType.TextToSpeechNode) updateSource(nodeData, 'tts_model_id_type')
    else if (node.type === WorkflowNodeType.RerankerNode) updateSource(nodeData, 'reranker_model_id_type')
    else if (nodeData.model_id_type !== undefined) updateSource(nodeData, 'model_id_type')

    if (node.type === WorkflowNodeType.LoopNode && nodeData.loop_body?.nodes) pendingNodes.push(...nodeData.loop_body.nodes)
  }
  return changedCount
}

function handleApplyToAll() {
  if (props.readonly || !props.workflowRef || applying.value) return
  applying.value = true
  return MsgConfirm('应用到所有节点', '将所有支持的节点（包括循环体内节点）切换为使用默认模型，是否继续？', {
    type: 'warning',
    confirmButtonText: '应用',
    confirmButtonType: 'primary',
  })
    .then(() => {
      if (props.readonly || !props.show) return
      const graph = props.workflowRef?.getGraphData()
      if (!graph) return
      const changedCount = applyDefaultSources(graph)
      if (changedCount > 0) props.workflowRef?.renderGraphData(graph)
      MsgSuccess(changedCount > 0 ? `已将 ${changedCount} 项模型配置切换为默认模型` : '所有适用节点已使用默认模型')
    })
    .catch(() => {})
    .finally(() => {
      applying.value = false
    })
}

// 关闭面板：保存、丢弃与取消分别处理，避免重复弹出确认框。
const confirmingClose = ref(false)

function handleClickOutside(event: MouseEvent) {
  if (!props.show || confirmingClose.value || applying.value) return
  const target = event.target
  if (target instanceof Element && target.closest('.el-overlay')) return
  if (!hasChanges.value) {
    emit('close')
    return
  }

  confirmingClose.value = true
  return MsgConfirm('提示', '默认模型设置尚未保存，是否保存修改？', {
    confirmButtonText: '保存修改',
    cancelButtonText: '不保存',
    confirmButtonType: 'primary',
    distinguishCancelAndClose: true,
  })
    .then(() => {
      handleSave()
      emit('close')
    })
    .catch((action: unknown) => {
      if (action !== 'cancel') return
      resetSettings()
      emit('close')
    })
    .finally(() => {
      confirmingClose.value = false
    })
}
</script>

<template>
  <div v-if="show" v-click-outside="handleClickOutside" class="w-100 max-w-full rounded-md border bg-white shadow-lg">
    <div class="p-3">
      <h4 class="mb-1">默认模型设置</h4>
      <p class="text-sm text-N600">配置各类型节点使用的默认模型，节点选择默认模型时将使用此处设置。</p>
    </div>
    <el-scrollbar max-height="calc(100vh - 220px)">
      <el-form v-loading="loading" label-position="top" class="px-3" :disabled="readonly" @submit.prevent>
        <el-form-item v-for="modelType in defaultModelTypes" :key="modelType.type" :label="modelType.label">
          <ModelSelect
            v-model="modelSettings[modelType.type].model_id"
            v-model:model-params="modelSettings[modelType.type].model_params_setting"
            :options="modelOptions[modelType.type] ?? []"
            :provider-options="providerOptions"
            :show-model-params="modelType.type !== 'RERANKER'"
            :disabled="readonly"
            placeholder="请选择模型"
            @change="handleModelChange(modelType.type)"
          />
        </el-form-item>
      </el-form>
    </el-scrollbar>
    <div class="flex-between gap-3 border-t p-3">
      <el-button :disabled="readonly || !workflowRef || confirmingClose" :loading="applying" @click="handleApplyToAll">应用到所有节点</el-button>
      <el-button type="primary" :disabled="readonly || !hasChanges || confirmingClose || applying" @click="handleSave">保存</el-button>
    </div>
  </div>
</template>
