<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, useTemplateRef } from 'vue'
import type { FormItemInstance } from 'element-plus'
import type { DefaultModelType, ModelItem, ModelProviderItem } from '@/api/types'
import SelectModel from '@/components/business/select-model/index.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { NodeModelData, NodeModelFields, NodeModelSource } from './types'

defineOptions({ name: 'NodeModelSelect' })

const props = withDefaults(
  defineProps<{
    nodeModel: WorkflowNodeModel
    formData: NodeModelData
    fields?: NodeModelFields
    canEditParams?: boolean
    canAdd?: boolean
    modelType: DefaultModelType
    label: string
    options: ModelItem[]
    providerOptions: ModelProviderItem[]
  }>(),
  {
    canEditParams: true,
    canAdd: false,
    fields: () => ({ source: 'model_id_type', id: 'model_id', reference: 'model_id_reference', params: 'model_params_setting' }),
  },
)
const emit = defineEmits<{ update: [patch: Partial<NodeModelData>]; refresh: [] }>()
const formItemRef = useTemplateRef<FormItemInstance>('formItemRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')

// 默认配置只用于展示与校验，不写入节点保留的自定义配置。
const source = computed(() => props.formData[props.fields.source])
const defaultModel = computed(() => props.nodeModel.getDefaultModelConfig(props.modelType))
const modelId = computed(() => props.formData[props.fields.id] ?? '')
const reference = computed(() => props.formData[props.fields.reference] ?? [])
const formProp = computed(() => (source.value === 'reference' ? props.fields.reference : props.fields.id))

function changeSource(value: NodeModelSource) {
  emit('update', { [props.fields.source]: value, [props.fields.reference]: [] })
  nextTick(() => formItemRef.value?.clearValidate())
}

function updateModelParams(params: Record<string, unknown>) {
  if (props.canEditParams && props.fields.params) emit('update', { [props.fields.params]: params })
}

// 注册到节点的外层表单，引用有效性失败也由同一个表单项展示。
async function validateModel() {
  if (source.value === 'reference') {
    if (!reference.value.length) throw new Error('请选择引用变量')
    await nextTick()
    if (!modelCascaderRef.value) throw new Error('请选择引用变量')
    await modelCascaderRef.value.validate().catch((error: unknown) => {
      throw error instanceof Error ? error : new Error(String(error))
    })
    return
  }
  if (source.value === 'default') {
    if (!defaultModel.value?.model_id) throw new Error(`请在默认模型设置中选择${props.label}`)
  } else if (!modelId.value) {
    throw new Error(`请选择${props.label}`)
  }
}

// 来源和模型下拉共用锚点保护；变量下拉由 NodeCascader 自行管理。
const anchorGuard = createAnchorGuard(props.nodeModel)
onBeforeUnmount(() => anchorGuard.reset())
</script>

<template>
  <el-form-item ref="formItemRef" class="mk-hide-asterisk" :prop="formProp" :rules="{ validator: validateModel, trigger: 'change' }">
    <template #label>
      <div class="flex-between gap-3">
        <span class="mk-required">{{ label }}</span>
        <el-select
          :model-value="source"
          :teleported="false"
          :validate-event="false"
          class="w-22!"
          size="small"
          @update:model-value="changeSource"
          @visible-change="anchorGuard.setOverlayVisible('model-source', $event)"
          @wheel="handleNodeWheel"
        >
          <el-option label="默认模型" value="default" />
          <el-option label="引用变量" value="reference" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </div>
    </template>
    <SelectModel
      v-if="source === 'default'"
      :model-value="defaultModel?.model_id ?? ''"
      :model-params="defaultModel?.model_params_setting ?? {}"
      :options="options"
      :provider-options="providerOptions"
      disabled
      placeholder="未配置默认模型"
    />
    <SelectModel
      v-else-if="source === 'custom'"
      :model-value="modelId"
      :model-params="fields.params ? formData[fields.params] : undefined"
      :options="options"
      :provider-options="providerOptions"
      :can-edit-params="canEditParams && !!fields.params"
      :can-add="canAdd"
      :placeholder="`请选择${label}`"
      @update:model-value="emit('update', { [fields.id]: $event })"
      @update:model-params="updateModelParams"
      @refresh="emit('refresh')"
      @visible-change="anchorGuard.setOverlayVisible('model', $event)"
      @wheel="handleNodeWheel"
    />
    <NodeCascader
      v-else
      ref="modelCascaderRef"
      :model-value="reference"
      :node-model="nodeModel"
      placeholder="请选择变量"
      @update:model-value="emit('update', { [fields.reference]: $event })"
    />
  </el-form-item>
</template>
