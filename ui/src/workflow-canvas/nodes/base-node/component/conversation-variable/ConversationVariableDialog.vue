<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ChatInputField } from '../../types'
import type { FormInstance } from 'element-plus'

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [data: ChatInputField, index?: number] }>()
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const formRef = useTemplateRef<FormInstance>('formRef')
const currentField = ref<ChatInputField>(createField())

function createField(): ChatInputField {
  return { field: '', label: '' }
}

function open(field?: ChatInputField, index?: number) {
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
        prop="field"
        :rules="[
          { whitespace: true, required: true, message: t('dynamicForm.fields.parameter.requiredMessage'), trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: t('workflow.parameters.invalidMessage'), trigger: 'blur' },
        ]"
      >
        <el-input
          v-model="currentField.field"
          maxlength="64"
          show-word-limit
          :placeholder="t('dynamicForm.fields.parameter.placeholder')"
          @blur="currentField.field = currentField.field.trim()"
        />
      </el-form-item>
      <el-form-item
        :label="t('dynamicForm.fields.displayName.label')"
        prop="label"
        :rules="{ whitespace: true, required: true, message: t('dynamicForm.fields.displayName.requiredMessage'), trigger: 'blur' }"
      >
        <el-input v-model="currentField.label" maxlength="64" show-word-limit :placeholder="t('dynamicForm.fields.displayName.placeholder')" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消参数编辑 -->
      <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确认参数编辑 -->
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? t('common.actions.add') : t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
