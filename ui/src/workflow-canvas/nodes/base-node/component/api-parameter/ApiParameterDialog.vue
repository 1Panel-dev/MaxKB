<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ApiInputField } from '../../types'
import type { FormInstance } from 'element-plus'

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [data: ApiInputField, index?: number] }>()
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const formRef = useTemplateRef<FormInstance>('formRef')
const currentField = ref<ApiInputField>(createField())

function createField(): ApiInputField {
  return { assignment_method: 'api_input', default_value: '', desc: '', is_required: true, type: 'input', variable: '' }
}

function open(field?: ApiInputField, index?: number) {
  if (field) currentField.value = cloneDeep(field)
  editingIndex.value = index
  dialogVisible.value = true
}

function submitField() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(currentField.value), editingIndex.value))
    .catch(() => {})
}

function resetData() {
  editingIndex.value = undefined
  currentField.value = createField()
  formRef.value?.clearValidate()
}

function close() {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog
    v-model="dialogVisible"
    :title="editingIndex === undefined ? t('common.parameters.add') : t('common.parameters.edit')"
    @closed="resetData"
  >
    <el-form
      :validate-on-rule-change="false"
      ref="formRef"
      :model="currentField"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item
        :label="t('dynamicForm.fields.parameter.label')"
        prop="variable"
        :rules="[
          { whitespace: true, required: true, message: t('dynamicForm.fields.parameter.requiredMessage'), trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: t('workflow.parameters.invalidMessage'), trigger: 'blur' },
        ]"
      >
        <el-input
          v-model="currentField.variable"
          maxlength="64"
          show-word-limit
          @blur="currentField.variable = currentField.variable.trim()"
          :placeholder="t('dynamicForm.fields.parameter.placeholder')"
        />
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input v-model="currentField.desc" maxlength="64" show-word-limit :placeholder="t('common.description.placeholder')" />
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.required.label')"><el-switch v-model="currentField.is_required" size="small" /></el-form-item>
      <el-form-item
        :label="t('dynamicForm.fields.defaultValue.label')"
        prop="default_value"
        :rules="{ required: currentField.is_required, message: t('dynamicForm.fields.defaultValue.requiredMessage'), trigger: 'blur' }"
      >
        <el-input v-model="currentField.default_value" :placeholder="t('dynamicForm.fields.defaultValue.placeholder')" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消参数编辑 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确定参数编辑 -->
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? t('common.actions.add') : t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
