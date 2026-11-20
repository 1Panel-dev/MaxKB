<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ParameterField } from './types'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'ParameterExtractionFieldDialog' })
const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [data: ParameterField, index?: number] }>()

const parameterTypeOptions = ['string', 'number', 'object', 'boolean', 'array'].map((type) => ({ value: type, label: type }))
const formRef = useTemplateRef<FormInstance>('formRef')
const editing = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const formData = ref<ParameterField>({ field: '', label: '', parameter_type: '', desc: '' })

const rules = computed<FormRules<ParameterField>>(() => ({
  field: [
    { whitespace: true, required: true, message: t('dynamicForm.fields.parameter.requiredMessage'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: t('workflow.parameterExtraction.parameters.invalidMessage'), trigger: 'blur' },
  ],
  label: [{ whitespace: true, required: true, message: t('dynamicForm.fields.displayName.requiredMessage'), trigger: 'blur' }],
  parameter_type: [{ required: true, message: t('workflow.parameterExtraction.type.requiredMessage'), trigger: 'change' }],
}))

const visible = ref(false)

function open(data?: ParameterField, index?: number) {
  if (data) {
    formData.value = cloneDeep(data)
    editing.value = true
    currentIndex.value = index
  }
  visible.value = true
}

function handleSubmit() {
  formRef.value
    ?.validate()
    .then(() => {
      emit('submit', cloneDeep(formData.value), currentIndex.value)
    })
    .catch(() => {})
}

function close() {
  visible.value = false
}

function resetData() {
  editing.value = false
  currentIndex.value = undefined
  formData.value = { field: '', label: '', parameter_type: '', desc: '' }
  formRef.value?.clearValidate()
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog v-model="visible" :title="editing ? t('common.parameters.edit') : t('common.parameters.add')" @closed="resetData">
    <el-form
      ref="formRef"
      label-position="top"
      require-asterisk-position="right"
      :rules="rules"
      :model="formData"
      :validate-on-rule-change="false"
      @submit.prevent
    >
      <el-form-item :label="t('dynamicForm.fields.parameter.label')" prop="field">
        <el-input v-model="formData.field" :maxlength="64" :placeholder="t('dynamicForm.fields.parameter.placeholder')" show-word-limit />
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.displayName.label')" prop="label">
        <el-input v-model="formData.label" :maxlength="64" :placeholder="t('dynamicForm.fields.displayName.placeholder')" show-word-limit />
      </el-form-item>
      <el-form-item :label="t('workflow.parameterExtraction.type.label')" prop="parameter_type">
        <el-select v-model="formData.parameter_type" :placeholder="t('workflow.parameterExtraction.type.placeholder')" class="w-full">
          <el-option v-for="item in parameterTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('common.description.label')" prop="desc">
        <el-input v-model="formData.desc" type="textarea" :rows="3" :placeholder="t('common.description.placeholder')" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消编辑提取参数 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存提取参数 -->
      <el-button type="primary" @click="handleSubmit">{{ editing ? t('common.actions.save') : t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
