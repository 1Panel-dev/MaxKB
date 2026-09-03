<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { Operation } from '@element-plus/icons-vue'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { AiModelSetting, AiModelSource } from '../../types'
import ModelParamsDialog from './ModelParamsDialog.vue'

defineOptions({ name: 'AiChatNodeModelSetting' })

const props = defineProps<{
  modelOptions: ModelItem[]
  nodeModel: WorkflowNodeModel
  providerOptions: ModelProviderItem[]
  setting: AiModelSetting
}>()
const emit = defineEmits<{ update: [setting: AiModelSetting] }>()

const nodeCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('nodeCascaderRef')
const paramsDialogRef = useTemplateRef<InstanceType<typeof ModelParamsDialog>>('paramsDialogRef')
let modelChangeSequence = 0

const modelFormProp = computed(() => (props.setting.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'))
const modelRequired = computed(() => props.setting.model_id_type !== 'default')

function updateSetting(changes: Partial<AiModelSetting>) {
  emit('update', { ...props.setting, ...changes })
}

function changeSource(source: AiModelSource) {
  updateSetting({ model_id_reference: [], model_id_type: source })
}

function changeModel(modelId: string) {
  const sequence = ++modelChangeSequence
  if (!modelId) {
    updateSetting({ model_id: '', model_params_setting: {} })
    return
  }
  updateSetting({ model_id: modelId, model_params_setting: {} })
  paramsDialogRef.value?.resetDefault(modelId).then((defaults) => {
    if (sequence !== modelChangeSequence) return
    updateSetting({ model_id: modelId, model_params_setting: defaults })
  })
}

function validate() {
  return props.setting.model_id_type === 'reference' ? nodeCascaderRef.value?.validate() : Promise.resolve()
}

defineExpose({ validate })
</script>

<template>
  <el-form-item
    :prop="modelFormProp"
    :rules="{ required: modelRequired, message: setting.model_id_type === 'reference' ? '请选择引用变量' : '请选择 AI 模型', trigger: 'change' }"
  >
    <template #label>
      <div class="flex-between w-full gap-3">
        <span>AI 模型</span>
        <el-select :model-value="setting.model_id_type" :teleported="false" class="w-24!" size="small" @update:model-value="changeSource">
          <el-option label="默认模型" value="default" />
          <el-option label="引用变量" value="reference" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </div>
    </template>

    <div v-if="setting.model_id_type === 'custom'" class="flex w-full items-center gap-2">
      <ModelSelect
        :model-value="setting.model_id"
        :options="modelOptions"
        :provider-options="providerOptions"
        placeholder="请选择 AI 模型"
        @change="changeModel"
      />
      <el-button :disabled="!setting.model_id" title="模型参数设置" @click="paramsDialogRef?.open(setting.model_id, setting.model_params_setting)">
        <MkIcon :icon="Operation" />
      </el-button>
    </div>

    <el-alert
      v-else-if="setting.model_id_type === 'default'"
      class="w-full"
      :closable="false"
      show-icon
      title="使用智能体配置的默认 LLM 模型"
      type="info"
    />

    <NodeCascader
      v-else
      ref="nodeCascaderRef"
      :model-value="setting.model_id_reference"
      :node-model="nodeModel"
      class="w-full"
      placeholder="请选择变量"
      @update:model-value="updateSetting({ model_id_reference: $event })"
    />
  </el-form-item>

  <ModelParamsDialog ref="paramsDialogRef" @submit="updateSetting({ model_params_setting: $event })" />
</template>
