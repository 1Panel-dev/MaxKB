<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'
import { cloneDeep, isEqual } from 'lodash'
import type LogicFlow from '@logicflow/core'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import type ModelApi from '@/api/admin/workspace/model/model'
import ModelProviderApi from '@/api/admin/model-provider'
import type { DefaultModelType, ModelConfig, ModelItem, ModelProviderItem } from '@/api/types'
import ModelSelect from '@/components/business/model-select/index.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { MODEL_TYPE_LABELS } from '@/constants/model'

defineOptions({ name: 'DefaultModelSettingDrawer' })

const defaultModelTypes = ['LLM', 'TTS', 'STT', 'IMAGE', 'TTI', 'TTV', 'ITV', 'RERANKER'] as const

const props = defineProps<{
  modelValue?: Partial<Record<DefaultModelType, ModelConfig>>
  modelApi: typeof ModelApi
  getGraphData: () => LogicFlow.GraphData | undefined
  disabled?: boolean
}>()
const emit = defineEmits<{
  save: [settings: Partial<Record<DefaultModelType, ModelConfig>>]
  applyToAll: [graphData: LogicFlow.GraphData]
  closed: []
}>()

const visible = ref(false)
const savedSettings = ref<Partial<Record<DefaultModelType, ModelConfig>>>({})

// 模型资源：调用方选择当前范围的完整 API，组件不通过 URL 推断资源范围。
const models = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const loading = ref(false)

provide('getModelParamsForm', (modelId: string) => props.modelApi.getModelParamsForm(modelId))

function loadModelOptions() {
  loading.value = true
  models.value = []
  providerOptions.value = []
  const providerRequest = ModelProviderApi.getProviderList().then((providers) => {
    providerOptions.value = providers
  })
  const modelRequest = props.modelApi.getModelList().then((modelList) => {
    models.value = modelList
  })
  // 模型列表只查询一次，各类型选择器从完整列表中过滤选项。
  return Promise.all([providerRequest, modelRequest]).finally(() => {
    loading.value = false
  })
}

function getModelOptions(modelType: DefaultModelType) {
  return models.value.filter((model) => model.model_type === modelType)
}

// 暂存模型设置：编辑和参数弹窗只修改副本，保存时才通知页面提交。
function normalizeSettings(settings: Partial<Record<DefaultModelType, ModelConfig>>) {
  return Object.fromEntries(
    defaultModelTypes.map((type) => [
      type,
      {
        ...cloneDeep(settings[type]),
        model_id: settings[type]?.model_id || '',
        model_params_setting: cloneDeep(settings[type]?.model_params_setting || {}),
      },
    ]),
  ) as Record<DefaultModelType, Required<ModelConfig>>
}

const modelSettings = ref(normalizeSettings(savedSettings.value))
const hasChanges = computed(() => !isEqual(modelSettings.value, normalizeSettings(savedSettings.value)))

// 接口保存成功后详情配置更新，只刷新比较基准，保留保存期间继续编辑的内容。
watch(
  () => props.modelValue,
  (settings) => {
    savedSettings.value = cloneDeep(settings ?? {})
  },
)

function resetSettings() {
  modelSettings.value = normalizeSettings(savedSettings.value)
}

function handleModelChange(modelType: DefaultModelType) {
  modelSettings.value[modelType].model_params_setting = {}
}

function handleSave() {
  if (props.disabled || !hasChanges.value) return
  emit('save', cloneDeep(modelSettings.value))
}

// 应用默认来源：保留自定义模型配置，并递归处理循环体中的节点。
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
const applying = ref(false)

function handleApplyToAll() {
  if (props.disabled || applying.value) return
  applying.value = true
  return MsgConfirm('应用到所有节点', '将把所有节点的模型来源统一改为「默认模型」，会覆盖它们当前的「自定义 / 引用变量」，请谨慎操作。', {
    type: 'warning',
    confirmButtonText: '应用',
    confirmButtonType: 'primary',
  })
    .then(() => {
      if (props.disabled || !visible.value) return
      const currentGraph = props.getGraphData()
      if (!currentGraph) return
      const graphData = cloneDeep(currentGraph)
      const changedCount = applyDefaultSources(graphData)
      if (changedCount > 0) emit('applyToAll', graphData)
      MsgSuccess('应用成功!')
    })
    .catch(() => {})
    .finally(() => {
      applying.value = false
    })
}

function open(settings: Partial<Record<DefaultModelType, ModelConfig>> = {}) {
  savedSettings.value = cloneDeep(settings)
  resetSettings()
  visible.value = true
  loadModelOptions()
}

function handleClosed() {
  resetData()
  emit('closed')
}

function resetData() {
  savedSettings.value = {}
  modelSettings.value = normalizeSettings({})
  models.value = []
  providerOptions.value = []
  loading.value = false
  applying.value = false
}

function handleBeforeClose(
  done = () => {
    visible.value = false
  },
) {
  if (!hasChanges.value) {
    done()
    return
  }
  return MsgConfirm('提示', '默认模型设置尚未保存，是否保存修改？', {
    confirmButtonText: '保存',
    cancelButtonText: '直接关闭',
    confirmButtonType: 'primary',
    distinguishCancelAndClose: true,
  })
    .then(() => {
      handleSave()
    })
    .catch((action) => {
      if (action === 'cancel') done()
    })
}
defineExpose({ open })
</script>

<template>
  <MkDrawer
    v-model="visible"
    title="默认模型设置"
    size="420"
    class="top-header! h-layout-content! max-w-full rounded-tl-xl!"
    :modal="false"
    :lock-scroll="false"
    :before-close="handleBeforeClose"
    @closed="handleClosed"
  >
    <template #header>
      <div>
        <h4 class="mb-1">默认模型设置</h4>
        <p class="text-sm text-N600">节点选择「默认模型」时，将使用以下配置</p>
      </div>
    </template>

    <el-form v-loading="loading" label-position="top" @submit.prevent>
      <el-form-item v-for="modelType in defaultModelTypes" :key="modelType" :label="MODEL_TYPE_LABELS[modelType]">
        <ModelSelect
          v-model="modelSettings[modelType].model_id"
          v-model:model-params="modelSettings[modelType].model_params_setting"
          :options="getModelOptions(modelType)"
          :provider-options="providerOptions"
          can-add
          @refresh="loadModelOptions"
          :can-edit-params="modelType !== 'RERANKER'"
          @change="handleModelChange(modelType)"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex-between gap-3">
        <el-button :disabled="disabled" :loading="applying" @click="handleApplyToAll">应用到所有节点</el-button>
        <div class="flex items-center">
          <el-button :disabled="applying" @click="visible = false">取消</el-button>
          <el-button type="primary" :disabled="disabled || !hasChanges || applying" @click="handleSave">保存</el-button>
        </div>
      </div>
    </template>
  </MkDrawer>
</template>
