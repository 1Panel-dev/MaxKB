<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { FormInstance, FormItemRule } from 'element-plus'
import { TRIGGER_PARAMETER_SOURCE, TRIGGER_TYPE } from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerBodyField, TriggerParameters, TriggerTaskSource, TriggerType } from '@/api/types'
import { type TaskParameterField, getTaskParameterFields, getTaskParameter, initializeTaskParameters } from './task-parameters'

const props = defineProps<{
  disabled?: boolean
  source: TriggerTaskSource
  resource?: Partial<ApplicationDetail & ToolItem>
  triggerType: TriggerType
  body: TriggerBodyField[]
}>()
const parameters = defineModel<TriggerParameters>({ required: true })
const formRef = ref<FormInstance>()
const fields = computed(() => getTaskParameterFields(props.source, props.resource))
const referenceOptions = computed(() => [
  { label: 'body', value: 'body', children: props.body.filter(({ field }) => field.trim()).map(({ field }) => ({ label: field, value: field })) },
])
watch(
  fields,
  (fields) => {
    initializeTaskParameters(parameters.value, fields)
  },
  { immediate: true },
)

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
  <el-form ref="formRef" :model="parameters" :disabled="disabled" label-position="top" @submit.prevent>
    <el-form-item
      v-for="field in fields"
      :key="JSON.stringify(field.path)"
      :prop="[...field.path, 'value']"
      :label="field.label"
      :rules="getParameterRules(field)"
    >
      <div class="flex w-full gap-2">
        <el-select
          v-model="getTaskParameter(parameters, field).source"
          class="w-24! shrink-0"
          @change="getTaskParameter(parameters, field).value = ''"
        >
          <el-option label="自定义" :value="TRIGGER_PARAMETER_SOURCE.CUSTOM" />
          <el-option label="引用" :value="TRIGGER_PARAMETER_SOURCE.REFERENCE" :disabled="triggerType !== TRIGGER_TYPE.EVENT || !body.length" />
        </el-select>
        <el-cascader
          v-if="getTaskParameter(parameters, field).source === TRIGGER_PARAMETER_SOURCE.REFERENCE"
          v-model="getTaskParameter(parameters, field).value"
          :options="referenceOptions"
          class="flex-1"
        />
        <el-input v-else v-model="getTaskParameter(parameters, field).value" :placeholder="`请输入${field.label}`" />
      </div>
    </el-form-item>
  </el-form>
</template>
