<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { LlmToolParameter } from '../types'
import type { FormInstance, FormRules } from 'element-plus'
import { toolParameterTypes } from '../types'

defineOptions({ name: 'WorkflowLlmToolParameterDialog' })

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ submit: [parameter: LlmToolParameter, index?: number] }>()
const formRef = useTemplateRef<FormInstance>('formRef')
const visible = ref(false)
const currentIndex = ref<number>()
const formData = ref<LlmToolParameter>(createParameter())
const rules = computed<FormRules<LlmToolParameter>>(() => ({
  name: [{ whitespace: true, required: true, message: t('dynamicForm.fields.parameter.requiredMessage'), trigger: 'blur' }],
  type: [{ required: true, message: t('workflow.llm.dataType.requiredMessage'), trigger: 'change' }],
}))

function createParameter(): LlmToolParameter {
  return { name: '', type: 'string', description: '', required: true }
}

function open(parameter?: LlmToolParameter, index?: number) {
  if (parameter) formData.value = cloneDeep(parameter)
  currentIndex.value = index
  visible.value = true
}

function close() {
  visible.value = false
}

function handleSubmit() {
  formData.value.name = formData.value.name.trim()
  formRef.value
    ?.validate()
    .then(() => emit('submit', cloneDeep(formData.value), currentIndex.value))
    .catch(() => {})
}

function resetData() {
  formData.value = createParameter()
  currentIndex.value = undefined
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="currentIndex === undefined ? t('workflow.llm.toolParameters.addTitle') : t('workflow.llm.toolParameters.editTitle')"
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
      @paste.stop
    >
      <el-form-item :label="t('dynamicForm.fields.parameter.label')" prop="name">
        <el-input
          v-model="formData.name"
          maxlength="64"
          show-word-limit
          :placeholder="t('dynamicForm.fields.parameter.placeholder')"
          @blur="formData.name = formData.name.trim()"
        />
      </el-form-item>
      <el-form-item :label="t('common.labels.dataType')" prop="type">
        <el-select v-model="formData.type" :placeholder="t('workflow.llm.dataType.placeholder')" class="w-full">
          <el-option v-for="parameterType in toolParameterTypes" :key="parameterType" :label="parameterType" :value="parameterType" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          maxlength="256"
          show-word-limit
          :placeholder="t('common.description.placeholder')"
        />
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.required.label')">
        <!-- 设置参数是否必填 -->
        <el-switch v-model="formData.required" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消参数编辑 -->
      <el-button plain @click="close">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存工具参数 -->
      <el-button type="primary" @click="handleSubmit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
