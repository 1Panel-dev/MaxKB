<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { TriggerBodyField } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ fields: TriggerBodyField[] }>()
const emit = defineEmits<{ submit: [field: TriggerBodyField, index?: number] }>()
const bodyFieldTypeOptions: TriggerBodyField['type'][] = ['string', 'int', 'dict', 'array', 'float', 'boolean']
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const editingIndex = ref<number>()
const createDefaultField = (): TriggerBodyField => ({ field: '', type: 'string', desc: '', required: false })
const formData = ref<TriggerBodyField>(createDefaultField())
const rules = computed<FormRules<TriggerBodyField>>(() => ({
  field: [
    { required: true, whitespace: true, message: t('trigger.requestParameters.name.requiredMessage'), trigger: 'blur' },
    {
      validator: (_rule, value: string, callback) => {
        const duplicate = props.fields.some((field, index) => index !== editingIndex.value && field.field.trim() === value.trim())
        callback(duplicate ? new Error(t('trigger.requestParameters.name.duplicateMessage')) : undefined)
      },
      trigger: 'blur',
    },
  ],
  type: [{ required: true, message: t('trigger.requestParameters.dataType.requiredMessage'), trigger: 'change' }],
}))

function open(field?: TriggerBodyField, index?: number) {
  editingIndex.value = index
  formData.value = field ? cloneDeep(field) : createDefaultField()
  visible.value = true
}
function close() {
  visible.value = false
}
function resetData() {
  formData.value = createDefaultField()
  editingIndex.value = undefined
  formRef.value?.clearValidate()
}
function submit() {
  formData.value.field = formData.value.field.trim()
  formRef.value?.validate((valid) => {
    if (valid) emit('submit', cloneDeep(formData.value), editingIndex.value)
  })
}
defineExpose({ open, close })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="editingIndex === undefined ? t('trigger.requestParameters.addTitle') : t('trigger.requestParameters.editTitle')"
    @closed="resetData"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('trigger.requestParameters.name.label')" prop="field">
        <el-input v-model="formData.field" :placeholder="t('trigger.requestParameters.name.placeholder')" />
      </el-form-item>
      <el-form-item :label="t('trigger.requestParameters.dataType.label')" prop="type">
        <el-select v-model="formData.type" :placeholder="t('trigger.requestParameters.dataType.placeholder')">
          <el-option v-for="type in bodyFieldTypeOptions" :key="type" :label="type" :value="type" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('common.description.label')" prop="desc">
        <el-input v-model="formData.desc" type="textarea" :rows="3" :placeholder="t('common.description.placeholder')" />
      </el-form-item>

      <el-form-item :label="t('dynamicForm.fields.required.label')">
        <el-switch v-model="formData.required" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消请求参数编辑 -->
      <el-button plain @click="close">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确定请求参数 -->
      <el-button type="primary" @click="submit">{{ t('common.actions.comfirm') }}</el-button>
    </template>
  </MkDialog>
</template>
