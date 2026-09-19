<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { FormInstance, FormItemRule } from 'element-plus'
import { RESOURCE_TYPE, TRIGGER_TYPE } from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerBodyField, TriggerParameters, TriggerType } from '@/api/types'
import { get, set } from 'lodash'
import type { TriggerParameter } from '@/api/types'
interface TaskParameterField {
  path: string[]
  label: string
  required: boolean
  defaultValue: string
}

type TaskResource =
  | { type: typeof RESOURCE_TYPE.APPLICATION; data?: Partial<ApplicationDetail> }
  | { type: typeof RESOURCE_TYPE.TOOL; data?: Partial<ToolItem> }

const props = defineProps<{
  disabled?: boolean
  resource: TaskResource
  triggerType: TriggerType
  body: TriggerBodyField[]
}>()
function getApplicationFields(application?: Partial<ApplicationDetail>): TaskParameterField[] {
  const fields: TaskParameterField[] = [{ path: ['question'], label: 'Question', required: true, defaultValue: '' }]
  const properties = application?.work_flow?.nodes?.find((node) => node.type === 'base-node')?.properties ?? {}
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
}
function getToolFields(tool?: Partial<ToolItem>): TaskParameterField[] {
  const fields: TaskParameterField[] = (tool?.input_field_list ?? []).map((field) => ({
    path: [field.name],
    label: field.name,
    required: field.is_required,
    defaultValue: '',
  }))
  const properties = tool?.work_flow?.nodes?.find((node) => node.type === 'tool-base-node')?.properties ?? {}
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
}
const fields = computed(() =>
  props.resource.type === RESOURCE_TYPE.APPLICATION ? getApplicationFields(props.resource.data) : getToolFields(props.resource.data),
)

const parameters = defineModel<TriggerParameters>({ required: true })
const formRef = ref<FormInstance>()
const showSource = computed(() => props.triggerType === TRIGGER_TYPE.EVENT && props.body.some(({ field }) => field.trim()))
const referenceOptions = computed(() => [
  { label: 'body', value: 'body', children: props.body.filter(({ field }) => field.trim()).map(({ field }) => ({ label: field, value: field })) },
])
watch(
  [() => props.resource.type, () => props.resource.data, showSource],
  ([, , canReference]) => {
    initializeTaskParameters(parameters.value, fields.value)
    if (!canReference) resetUnavailableReferences(parameters.value, fields.value)
    formRef.value?.clearValidate()
  },
  { immediate: true },
)

/** 只补全缺失输入，编辑和折叠时不覆盖已保存参数。 */
function initializeTaskParameters(parameters: TriggerParameters, fields: TaskParameterField[]) {
  fields.forEach((field) => {
    if (!get(parameters, field.path)) set(parameters, field.path, { source: 'custom', value: field.defaultValue })
  })
  return parameters
}

function getTaskParameter(parameters: TriggerParameters, field: TaskParameterField): TriggerParameter {
  return get(parameters, field.path) as TriggerParameter
}

/** 引用来源不可用时恢复自定义默认值，不改动已有的自定义参数。 */
function resetUnavailableReferences(parameters: TriggerParameters, fields: TaskParameterField[]) {
  fields.forEach((field) => {
    const parameter = getTaskParameter(parameters, field)
    if (parameter.source === 'reference') {
      parameter.source = 'custom'
      parameter.value = field.defaultValue
    }
  })
}

function getParameterRules(field: TaskParameterField): FormItemRule[] {
  return [
    ...(getTaskParameter(parameters.value, field).source === 'custom'
      ? [{ whitespace: true, required: field.required, message: `请输入${field.label}`, trigger: 'change' }]
      : []),
    {
      validator: (_rule, _value, callback) => {
        const parameter = getTaskParameter(parameters.value, field)
        const value = parameter.value
        if (
          parameter.source === 'reference' &&
          (props.triggerType !== TRIGGER_TYPE.EVENT ||
            !Array.isArray(value) ||
            value.length !== 2 ||
            value[0] !== 'body' ||
            !props.body.some(({ field }) => field === value[1]))
        ) {
          callback(new Error('请选择有效的事件请求参数，或切换为自定义'))
        } else if (field.required && (Array.isArray(value) ? !value.length : !value?.trim())) {
          callback(new Error(`请输入${field.label}`))
        } else callback()
      },
      trigger: 'change',
    },
  ]
}

function validate() {
  return nextTick().then(() => formRef.value?.validate())
}
defineExpose({ validate })
</script>

<template>
  <el-form class="space-y-2!" ref="formRef" :model="parameters" :disabled="disabled" label-position="top" hide-required-asterisk @submit.prevent>
    <el-form-item
      v-for="field in fields"
      :key="JSON.stringify(field.path)"
      :prop="[...field.path, 'value']"
      :label="field.label"
      :rules="getParameterRules(field)"
    >
      <template #label>
        <div class="flex-between w-full">
          <span>{{ field.label }}<span v-if="field.required" class="ml-1 text-danger">*</span></span>
          <el-select
            v-if="showSource"
            v-model="getTaskParameter(parameters, field).source"
            :teleported="false"
            size="small"
            class="w-24!"
            @change="getTaskParameter(parameters, field).value = getTaskParameter(parameters, field).source === 'reference' ? [] : field.defaultValue"
          >
            <el-option label="引用" value="reference" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </div>
      </template>
      <el-cascader
        v-if="getTaskParameter(parameters, field).source === 'reference'"
        v-model="getTaskParameter(parameters, field).value"
        :options="referenceOptions"
        class="w-full"
        placeholder="请选择"
      />
      <el-input v-else v-model="getTaskParameter(parameters, field).value" :placeholder="`请输入${field.label}`" />
    </el-form-item>
  </el-form>
</template>
