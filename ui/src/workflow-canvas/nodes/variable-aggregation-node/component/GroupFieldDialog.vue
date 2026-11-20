<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'VariableAggregationGroupFieldDialog' })
const { t } = useI18n({ useScope: 'global' })

interface GroupFieldForm {
  field: string
  label: string
}

const emit = defineEmits<{ submit: [data: GroupFieldForm, index?: number] }>()

const formRef = useTemplateRef<FormInstance>('formRef')
const editing = ref(false)
const currentIndex = ref<number | undefined>(undefined)
const formData = ref<GroupFieldForm>({ field: '', label: '' })

const rules = computed<FormRules<GroupFieldForm>>(() => ({
  label: [{ whitespace: true, required: true, message: t('dynamicForm.fields.displayName.requiredMessage'), trigger: 'blur' }],
  field: [
    { whitespace: true, required: true, message: t('workflow.variable.requiredMessage'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: t('workflow.variable.invalidMessage'), trigger: 'blur' },
  ],
}))

const visible = ref(false)

function open(data?: GroupFieldForm, index?: number) {
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
  formData.value = { field: '', label: '' }
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="editing ? t('workflow.variableAggregation.group.edit') : t('workflow.variableAggregation.group.add')"
    @closed="resetData"
  >
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
    </el-form>
    <template #footer>
      <!-- 取消编辑聚合分组 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存聚合分组 -->
      <el-button type="primary" @click="handleSubmit">{{ editing ? t('common.actions.save') : t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
