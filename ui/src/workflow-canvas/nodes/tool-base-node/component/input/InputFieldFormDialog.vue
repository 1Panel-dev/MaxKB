<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ToolInputField } from '../../types'
import type { FormInstance, FormRules } from 'element-plus'

const { t } = useI18n({ useScope: 'global' })

const typeOptions = ['string', 'int', 'dict', 'array', 'float', 'boolean']
const emit = defineEmits<{ submit: [data: ToolInputField, index?: number] }>()
const formRef = useTemplateRef<FormInstance>('formRef')
const dialogVisible = ref(false)
const editingIndex = ref<number>()
const form = ref<ToolInputField>(createField())
const rules = computed<FormRules<ToolInputField>>(() => ({
  field: [{ whitespace: true, required: true, message: t('dynamicForm.fields.parameter.requiredMessage'), trigger: 'blur' }],
  label: [{ whitespace: true, required: true, message: t('dynamicForm.fields.displayName.requiredMessage'), trigger: 'blur' }],
}))

function createField(): ToolInputField {
  return { field: '', type: 'string', label: '', desc: '', is_required: true }
}

// 打开和关闭统一重置草稿，取消编辑不会影响下一次添加。
function resetData() {
  form.value = createField()
  editingIndex.value = undefined
  formRef.value?.clearValidate()
}

function open(field?: ToolInputField, index?: number) {
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
          :maxlength="64"
          show-word-limit
          @blur="form.field = form.field.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.displayName.label')" prop="label">
        <el-input
          v-model="form.label"
          :placeholder="t('dynamicForm.fields.displayName.placeholder')"
          :maxlength="128"
          show-word-limit
          @blur="form.label = form.label?.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="form.desc"
          :placeholder="t('common.description.placeholder')"
          :maxlength="128"
          show-word-limit
          @blur="form.desc = form.desc?.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('tool.inputParams.dataType.label')">
        <el-select v-model="form.type">
          <el-option v-for="fieldType in typeOptions" :key="fieldType" :label="fieldType" :value="fieldType" />
        </el-select>
      </el-form-item>

      <el-form-item :label="t('dynamicForm.fields.required.columnLabel')">
        <el-switch size="small" v-model="form.is_required" />
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
