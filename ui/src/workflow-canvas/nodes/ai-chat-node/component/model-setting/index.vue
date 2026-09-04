<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { AiModelSetting, AiModelSource } from '../../types'

defineOptions({ name: 'AiChatNodeModelSetting' })

const props = defineProps<{
  modelOptions: ModelItem[]
  nodeModel: WorkflowNodeModel
  providerOptions: ModelProviderItem[]
  setting: AiModelSetting
}>()
const emit = defineEmits<{ update: [setting: Partial<AiModelSetting>] }>()

const nodeCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('nodeCascaderRef')

const modelFormProp = computed(() => (props.setting.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'))

function updateSetting(changes: Partial<AiModelSetting>) {
  emit('update', changes)
}

function changeSource(source: AiModelSource) {
  updateSetting({ model_id_reference: [], model_id_type: source })
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  const { model_id_type, model_id, model_id_reference } = props.setting
  if (model_id_type === 'reference') {
    callback(model_id_reference.length ? undefined : new Error('请选择引用变量'))
    return
  }
  callback(model_id ? undefined : new Error(model_id_type === 'default' ? '请在默认模型设置中选择 AI 模型' : '请选择 AI 模型'))
}

function validate() {
  return props.setting.model_id_type === 'reference' ? nodeCascaderRef.value?.validate() : Promise.resolve()
}

defineExpose({ validate })
</script>

<template>
  <el-form-item class="mk-hide-asterisk" :prop="modelFormProp" :rules="{ validator: validateModel, trigger: 'change' }">
    <template #label>
      <div class="flex-between">
        <span class="mk-required">AI 模型</span>
        <el-select :model-value="setting.model_id_type" :teleported="false" class="w-22!" size="small" @update:model-value="changeSource">
          <el-option label="默认模型" value="default" />
          <el-option label="引用变量" value="reference" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </div>
    </template>
    <ModelSelect
      v-if="setting.model_id_type === 'default'"
      :model-value="setting.model_id"
      :model-params="setting.model_params_setting"
      :disabled="setting.model_id_type === 'default'"
      :options="modelOptions"
      :provider-options="providerOptions"
      placeholder="未配置默认模型"
    />
    <ModelSelect
      v-else-if="setting.model_id_type === 'custom'"
      :model-value="setting.model_id"
      :model-params="setting.model_params_setting"
      can-edit-params
      :options="modelOptions"
      :provider-options="providerOptions"
      placeholder="请选择 AI 模型"
      @update:model-value="updateSetting({ model_id: $event })"
      @update:model-params="updateSetting({ model_params_setting: $event })"
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
</template>
