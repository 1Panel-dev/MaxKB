<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { FormInstance, FormItemRule } from 'element-plus'
import { TRIGGER_PARAMETER_SOURCE, TRIGGER_TYPE } from '@/api/enums'
import type { TriggerBodyField, TriggerParameters, TriggerType } from '@/api/types'
import { get, set } from 'lodash'
import type { TriggerParameter } from '@/api/types'
import type { TaskParameterField } from './types'

const props = defineProps<{
  disabled?: boolean
  fields: TaskParameterField[]
  triggerType: TriggerType
  body: TriggerBodyField[]
}>()
const parameters = defineModel<TriggerParameters>({ required: true })
const formRef = ref<FormInstance>()
const showSource = computed(() => props.triggerType === TRIGGER_TYPE.EVENT && props.body.some(({ field }) => field.trim()))
const referenceOptions = computed(() => [
  { label: 'body', value: 'body', children: props.body.filter(({ field }) => field.trim()).map(({ field }) => ({ label: field, value: field })) },
])
watch(
  [() => props.fields, showSource],
  ([fields, canReference]) => {
    initializeTaskParameters(parameters.value, fields)
    if (!canReference) resetUnavailableReferences(parameters.value, fields)
    formRef.value?.clearValidate()
  },
  { immediate: true },
)

/** 只补全缺失输入，编辑和折叠时不覆盖已保存参数。 */
function initializeTaskParameters(parameters: TriggerParameters, fields: TaskParameterField[]) {
  fields.forEach((field) => {
    if (!get(parameters, field.path)) set(parameters, field.path, { source: TRIGGER_PARAMETER_SOURCE.CUSTOM, value: field.defaultValue })
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
    if (parameter.source === TRIGGER_PARAMETER_SOURCE.REFERENCE) {
      parameter.source = TRIGGER_PARAMETER_SOURCE.CUSTOM
      parameter.value = field.defaultValue
    }
  })
}

function getParameterRules(field: TaskParameterField): FormItemRule[] {
  return [
    {
      validator: (_rule, _value, callback) => {
        const parameter = getTaskParameter(parameters.value, field)
        const value = parameter.value
        if (
          parameter.source === TRIGGER_PARAMETER_SOURCE.REFERENCE &&
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
  <el-form ref="formRef" :model="parameters" :disabled="disabled" label-position="top" hide-required-asterisk @submit.prevent>
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
            @change="
              getTaskParameter(parameters, field).value =
                getTaskParameter(parameters, field).source === TRIGGER_PARAMETER_SOURCE.REFERENCE ? [] : field.defaultValue
            "
          >
            <el-option label="引用" :value="TRIGGER_PARAMETER_SOURCE.REFERENCE" />
            <el-option label="自定义" :value="TRIGGER_PARAMETER_SOURCE.CUSTOM" />
          </el-select>
        </div>
      </template>
      <el-cascader
        v-if="getTaskParameter(parameters, field).source === TRIGGER_PARAMETER_SOURCE.REFERENCE"
        v-model="getTaskParameter(parameters, field).value"
        :options="referenceOptions"
        class="w-full"
        placeholder="请选择"
      />
      <el-input v-else v-model="getTaskParameter(parameters, field).value" :placeholder="`请输入${field.label}`" />
    </el-form-item>
  </el-form>
</template>
