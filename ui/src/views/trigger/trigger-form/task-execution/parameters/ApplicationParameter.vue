<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { ApplicationDetail, TriggerBodyField, TriggerParameters, TriggerType } from '@/api/types'
import ParameterForm from './ParameterForm.vue'
import type { TaskParameterField } from './types'

const props = defineProps<{ application?: Partial<ApplicationDetail>; triggerType: TriggerType; body: TriggerBodyField[]; disabled?: boolean }>()
const parameters = defineModel<TriggerParameters>({ required: true })
const parameterFormRef = useTemplateRef<InstanceType<typeof ParameterForm>>('parameterFormRef')
// 生成当前资源的执行参数，保留各自的字段分组和默认值。
const fields = computed<TaskParameterField[]>(() => {
  const fields: TaskParameterField[] = [{ path: ['question'], label: 'Question', required: true, defaultValue: '' }]
  const properties = props.application?.work_flow?.nodes?.find((node) => node.type === 'base-node')?.properties ?? {}
  const nodeData = properties.node_data ?? {}
  if (nodeData.file_upload_enable) {
    const fileLabels = { document: '文档', image: '图片', audio: '音频', video: '视频', other: '其他文件' }
    Object.entries(fileLabels).forEach(([type, label]) => {
      if (nodeData.file_upload_setting?.[type]) fields.push({ path: [`${type}_list`], label, required: true, defaultValue: '[]' })
    })
  }
  const userFields = properties.user_input_field_list as
    | { field: string; required?: boolean; default_value?: unknown; label?: string | { label?: string } }[]
    | undefined
  userFields?.forEach((field) => {
    fields.push({
      path: ['user_input_field_list', field.field],
      label: (typeof field.label === 'string' ? field.label : field.label?.label) || field.field,
      required: field.required ?? false,
      defaultValue:
        typeof field.default_value === 'string' ? field.default_value : field.default_value === undefined ? '' : JSON.stringify(field.default_value),
    })
  })
  const apiFields = properties.api_input_field_list as { variable: string; is_required?: boolean; default_value?: unknown }[] | undefined
  apiFields?.forEach((field) => {
    fields.push({
      path: ['api_input_field_list', field.variable],
      label: field.variable,
      required: field.is_required ?? false,
      defaultValue:
        typeof field.default_value === 'string' ? field.default_value : field.default_value === undefined ? '' : JSON.stringify(field.default_value),
    })
  })
  return fields
})
function validate() {
  return parameterFormRef.value?.validate() ?? Promise.resolve(false)
}
defineExpose({ validate })
</script>

<template>
  <ParameterForm ref="parameterFormRef" v-model="parameters" :fields="fields" :trigger-type="triggerType" :body="body" :disabled="disabled" />
</template>
