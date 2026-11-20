<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ToolOutputField } from '../../types'
import type { FormInstance, FormRules } from 'element-plus'

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [data: ToolOutputField, index?: number] }>()
const formRef = useTemplateRef<FormInstance>('formRef')
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const form = ref<ToolOutputField>(createField())
const rules = computed<FormRules<ToolOutputField>>(() => ({
  field: [{ whitespace: true, required: true, message: t('dynamicForm.fields.parameter.requiredMessage'), trigger: 'blur' }],
}))

function createField(): ToolOutputField {
  return { field: '', type: 'string', label: '', is_required: true }
}

// 打开和关闭统一重置草稿，取消编辑不会影响下一次添加。
function resetData() {
  form.value = createField()
  editingIndex.value = undefined
  formRef.value?.clearValidate()
}

function open(field?: ToolOutputField, index?: number) {
  if (field) form.value = cloneDeep(field)
  editingIndex.value = index
  dialogVisible.value = true
}

function submitField() {
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(form.value), editingIndex.value))
    .catch(() => {})
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
      label-position="top"
      ref="formRef"
      :rules="rules"
      :model="form"
      :validate-on-rule-change="false"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('dynamicForm.fields.parameter.label')" prop="field">
        <el-input
          v-model="form.field"
          :placeholder="t('dynamicForm.fields.parameter.placeholder')"
          maxlength="64"
          show-word-limit
          @blur="form.field = form.field.trim()"
        />
      </el-form-item>

      <el-form-item :label="t('dynamicForm.fields.displayName.label')">
        <el-input
          v-model="form.label"
          :placeholder="t('dynamicForm.fields.displayName.placeholder')"
          :maxlength="128"
          show-word-limit
          @blur="form.label = form.label?.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span>
        <!-- 取消编辑 -->
        <el-button plain @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
        <!-- 提交参数 -->
        <el-button type="primary" @click="submitField">
          {{ editingIndex === undefined ? t('common.actions.add') : t('common.actions.save') }}
        </el-button>
      </span>
    </template>
  </MkDialog>
</template>
