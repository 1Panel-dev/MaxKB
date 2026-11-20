<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { VariableField } from './types'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'VariableSplittingFieldDialog' })
const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ submit: [data: VariableField, index?: number] }>()

const formRef = useTemplateRef<FormInstance>('formRef')
const editing = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const formData = ref<VariableField>({ field: '', label: '', expression: '' })

const rules = computed<FormRules<VariableField>>(() => ({
  label: [{ whitespace: true, required: true, message: t('dynamicForm.fields.displayName.requiredMessage'), trigger: 'blur' }],
  field: [
    { whitespace: true, required: true, message: t('workflow.variable.requiredMessage'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: t('workflow.variable.invalidMessage'), trigger: 'blur' },
  ],
  expression: [{ whitespace: true, required: true, message: t('workflow.variableSplitting.expression.requiredMessage'), trigger: 'blur' }],
}))

const visible = ref(false)

function open(data?: VariableField, index?: number) {
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
  formData.value = { field: '', label: '', expression: '' }
  formRef.value?.clearValidate()
}

defineExpose({ close, open })
</script>
<template>
  <MkDialog v-model="visible" :title="editing ? t('workflow.variable.edit') : t('workflow.variable.add')" @closed="resetData">
    <el-form
      ref="formRef"
      label-position="top"
      require-asterisk-position="right"
      :rules="rules"
      :model="formData"
      :validate-on-rule-change="false"
      @submit.prevent
    >
      <el-form-item :label="t('workflow.variable.label')" prop="field">
        <el-input v-model="formData.field" :maxlength="64" :placeholder="t('workflow.variable.placeholder')" show-word-limit />
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.displayName.label')" prop="label">
        <el-input v-model="formData.label" :maxlength="64" show-word-limit :placeholder="t('dynamicForm.fields.displayName.placeholder')" />
      </el-form-item>
      <el-form-item class="mk-hide-asterisk" prop="expression">
        <template #label>
          <span class="flex-align-center gap-1">
            <span class="mk-required">{{ t('workflow.variableSplitting.expression.label') }}</span>
            <MkTooltip placement="right">
              <template #content>
                {{ t('workflow.variableSplitting.expression.description', { example: '$.store.book' }) }}
                <!-- 查看 JSON Path 表达式文档 -->
                <a
                  href="https://pypi.org/project/jsonpath-ng/1.8.0/"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-primary hover:text-primary/80"
                >
                  {{ t('workflow.variableSplitting.expression.viewDetails') }} ➜ pypi.org
                </a>
              </template>
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </span>
        </template>
        <el-input
          v-model="formData.expression"
          :maxlength="64"
          show-word-limit
          :placeholder="t('workflow.variableSplitting.expression.placeholder')"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消编辑拆分变量 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存拆分变量 -->
      <el-button type="primary" @click="handleSubmit">{{ editing ? t('common.actions.save') : t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
