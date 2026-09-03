<script setup lang="ts">
import { inject, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { DynamicFormField } from '@/api/types'
import { MkDynamicsForm, type FormField } from '@/components/mk-dynamics-form'

defineOptions({ name: 'AiChatNodeModelParamsDialog' })

const emit = defineEmits<{ submit: [settings: Record<string, unknown>] }>()

const getModelParamsForm = inject<(modelId: string) => Promise<DynamicFormField[]>>('getModelParamsForm')
const visible = ref(false)
const loading = ref(false)
const formFields = ref<FormField[]>([])
const formData = ref<Record<string, unknown>>({})
const formRef = useTemplateRef<InstanceType<typeof MkDynamicsForm>>('formRef')

function getDefaultSettings(fields: DynamicFormField[]) {
  return fields.reduce<Record<string, unknown>>((settings, field) => {
    if (field.show_default_value !== false) settings[field.field] = cloneDeep(field.default_value)
    return settings
  }, {})
}

function load(modelId: string) {
  if (!getModelParamsForm) return Promise.resolve<Record<string, unknown>>({})
  loading.value = true
  return getModelParamsForm(modelId)
    .then((fields) => {
      formFields.value = fields as unknown as FormField[]
      return getDefaultSettings(fields)
    })
    .finally(() => {
      loading.value = false
    })
}

function open(modelId: string, settings?: Record<string, unknown>) {
  visible.value = true
  load(modelId).then((defaults) => {
    const validFields = new Set(formFields.value.map(({ field }) => field))
    const savedSettings = Object.fromEntries(Object.entries(settings ?? {}).filter(([field]) => validFields.has(field)))
    formData.value = { ...defaults, ...cloneDeep(savedSettings) }
  })
}

function resetDefault(modelId: string) {
  return load(modelId)
}

function submit() {
  formRef.value?.validate().then(() => {
    emit('submit', cloneDeep(formData.value))
    visible.value = false
  })
}

function resetData() {
  formFields.value = []
  formData.value = {}
  loading.value = false
}

defineExpose({ open, resetDefault })
</script>

<template>
  <MkDialog v-model="visible" title="模型参数设置" width="600" @closed="resetData">
    <div v-loading="loading">
      <MkDynamicsForm ref="formRef" v-model="formData" :render-data="formFields" default-item-width="100%" />
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
