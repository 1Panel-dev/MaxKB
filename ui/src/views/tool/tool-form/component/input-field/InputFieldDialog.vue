<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ToolInputField } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'InputFieldDialog' })

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ refresh: [field: ToolInputField, index?: number] }>()

const inputFieldTypeOptions: ToolInputField['type'][] = ['string', 'int', 'float', 'dict', 'array']
const formRef = ref<FormInstance>()
const visible = ref(false)
const isEdit = ref(false)
const inputFieldForm = reactive<ToolInputField>({ desc: '', is_required: true, name: '', source: 'reference', type: 'string' })
const formRules = computed<FormRules<ToolInputField>>(() => ({
  name: [{ whitespace: true, required: true, message: t('tool.inputParams.name.requiredMessage'), trigger: 'blur' }],
}))

function open(field?: ToolInputField) {
  if (field) {
    isEdit.value = true
    Object.assign(inputFieldForm, cloneDeep(field))
  }

  visible.value = true
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    emit('refresh', cloneDeep(inputFieldForm))
    visible.value = false
  })
}

function resetData() {
  isEdit.value = false
  Object.assign(inputFieldForm, { desc: '', is_required: true, name: '', source: 'reference', type: 'string' })
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog :align-center="false" v-model="visible" :title="isEdit ? t('common.parameters.edit') : t('common.parameters.add')" @closed="resetData">
    <el-form
      ref="formRef"
      :model="inputFieldForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('tool.inputParams.name.label')" prop="name">
        <el-input
          v-model="inputFieldForm.name"
          maxlength="64"
          :placeholder="t('tool.inputParams.name.placeholder')"
          @blur="inputFieldForm.name = inputFieldForm.name.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('tool.inputParams.dataType.label')">
        <el-select v-model="inputFieldForm.type" class="w-full">
          <el-option v-for="type in inputFieldTypeOptions" :key="type" :label="type" :value="type" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.tooltip.label')">
        <el-input
          v-model="inputFieldForm.desc"
          maxlength="128"
          show-word-limit
          :placeholder="t('dynamicForm.fields.tooltip.placeholder')"
          @blur="inputFieldForm.desc = inputFieldForm.desc?.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('tool.source.label')">
        <el-select v-model="inputFieldForm.source" class="w-full">
          <el-option :label="t('tool.source.reference')" value="reference" />
          <el-option :label="t('tool.source.custom')" value="custom" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.required.label')" @click.prevent><el-switch v-model="inputFieldForm.is_required" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" @click="handleSubmit">{{ isEdit ? t('common.actions.save') : t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
