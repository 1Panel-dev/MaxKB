<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { ToolItem, TriggerBodyField, TriggerParameters, TriggerType } from '@/api/types'
import ParameterForm from './ParameterForm.vue'
import type { TaskParameterField } from './types'

const props = defineProps<{ tool?: Partial<ToolItem>; triggerType: TriggerType; body: TriggerBodyField[]; disabled?: boolean }>()
const parameters = defineModel<TriggerParameters>({ required: true })
const parameterFormRef = useTemplateRef<InstanceType<typeof ParameterForm>>('parameterFormRef')
// 生成当前资源的执行参数，保留各自的字段分组和默认值。
const fields = computed<TaskParameterField[]>(() => {
  const fields: TaskParameterField[] = (props.tool?.input_field_list ?? []).map((field) => ({
    path: [field.name],
    label: field.name,
    required: field.is_required,
    defaultValue: '',
  }))
  const properties = props.tool?.work_flow?.nodes?.find((node) => node.type === 'tool-base-node')?.properties ?? {}
  const userFields = properties.user_input_field_list as
    | { field: string; is_required?: boolean; required?: boolean; default_value?: unknown; label?: string | { label?: string } }[]
    | undefined
  userFields?.forEach((field) => {
    fields.push({
      path: ['user_input_field_list', field.field],
      label: (typeof field.label === 'string' ? field.label : field.label?.label) || field.field,
      required: field.is_required ?? field.required ?? false,
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
