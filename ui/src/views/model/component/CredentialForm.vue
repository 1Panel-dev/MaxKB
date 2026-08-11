<template>
  <el-form ref="formRef" :model="localValue" label-position="top" require-asterisk-position="right">
    <template v-for="field in fields" :key="field.field">
      <CredentialFormItem
        :field="field"
        v-model="localValue"
        :form-value="localValue"
        @change="onFieldChange"
      />
    </template>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { FormField } from '@/api/type/common'
import type { FormInstance } from 'element-plus'
import CredentialFormItem from './CredentialFormItem.vue'
import providerApi from '@/api/model/provider'

const props = defineProps<{
  fields: FormField[]
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: Record<string, any>): void
}>()

const formRef = ref<FormInstance>()

const localValue = ref<Record<string, any>>({ ...(props.modelValue || {}) })

watch(() => props.modelValue, (val) => {
  localValue.value = { ...(val || {}) }
}, { deep: true })

watch(localValue, (val) => {
  emit('update:modelValue', { ...val })
}, { deep: true })

function setDefaultValues(fields: FormField[]) {
  for (const f of fields) {
    if (f.default_value !== undefined && f.default_value !== null && !(f.field in localValue.value)) {
      localValue.value[f.field] = f.default_value
    }
    if (f.children && f.children.length > 0) {
      setDefaultValues(f.children)
    }
  }
}

watch(() => props.fields, (fields) => {
  setDefaultValues(fields)
}, { immediate: true })

function onFieldChange(field: string, val: any) {
  // Check for trigger fields
  const changedField = props.fields.find(f => f.field === field)
  if (changedField?.relation_trigger_field_dict) {
    const triggerConfig = changedField.relation_trigger_field_dict
    for (const triggerField of Object.keys(triggerConfig)) {
      const allowedValues = triggerConfig[triggerField]
      const actualValue = String(val ?? '')
      if (allowedValues && Array.isArray(allowedValues)) {
        if (allowedValues.includes(actualValue)) {
          fetchOptionsForField(triggerField)
        }
      }
    }
  }
  emit('update:modelValue', { ...localValue.value })
}

function fetchOptionsForField(fieldName: string) {
  const targetField = props.fields.find(f => f.field === fieldName)
  if (targetField && targetField.method && targetField.provider) {
    providerApi.getModelCreateForm(
      targetField.provider,
      '',
      '',
    ).then((res) => {
      if (res.data && Array.isArray(res.data)) {
        const matched = res.data.find((f: any) => f.field === fieldName)
        if (matched?.option_list) {
          targetField.option_list = matched.option_list
        }
      }
    })
  }
}

async function validate(): Promise<boolean> {
  if (!formRef.value) return true
  try {
    await formRef.value.validate()
    return true
  } catch {
    return false
  }
}

defineExpose({ validate, formRef })
</script>
