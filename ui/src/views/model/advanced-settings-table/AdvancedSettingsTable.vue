<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, useTemplateRef } from 'vue'
import type { DynamicFormField } from '@/api/types'
import { dynamicFormTypeOptions, type FormField } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'
import ModelParamDialog from './ModelParamDialog.vue'

defineOptions({ name: 'ModelAdvancedSettings' })

const { t } = useI18n({ useScope: 'global' })

const modelParams = defineModel<DynamicFormField[]>({ required: true })

const currentIndex = ref<number>()
const modelParamDialogRef = useTemplateRef<InstanceType<typeof ModelParamDialog>>('modelParamDialogRef')

function handleOpenParamDialog(field?: DynamicFormField, index?: number) {
  currentIndex.value = index
  modelParamDialogRef.value?.open(field)
}

function getTypeLabel(inputType: string) {
  const label = dynamicFormTypeOptions.find((option) => option.value === inputType)?.label
  return label ? t(label) : inputType
}

function handleSubmitParam(field: FormField) {
  const label = typeof field.label === 'object' ? { ...field.label, label: field.label.label ?? field.field } : (field.label ?? field.field)
  const modelParam: DynamicFormField = { ...field, label }
  const duplicateField = modelParams.value.some((param, index) => param.field === modelParam.field && index !== currentIndex.value)
  if (duplicateField) {
    MsgError(t('dynamicForm.validation.duplicateParameter', { parameter: modelParam.field }))
    return
  }

  const modelParamLabel = typeof modelParam.label === 'string' ? modelParam.label : modelParam.label.label
  const duplicateLabel = modelParams.value.some(
    (param, index) => (typeof param.label === 'string' ? param.label : param.label.label) === modelParamLabel && index !== currentIndex.value,
  )
  if (duplicateLabel) {
    MsgError(t('dynamicForm.validation.duplicateDisplayName', { displayName: modelParamLabel }))
    return
  }

  if (currentIndex.value === undefined) {
    modelParams.value.push(modelParam)
  } else {
    modelParams.value.splice(currentIndex.value, 1, modelParam)
  }
  modelParamDialogRef.value?.close()
}

function handleDeleteParam(index: number) {
  modelParams.value.splice(index, 1)
}
</script>

<template>
  <div class="flex-between mb-2">
    <span>{{ t('model.parameters.title') }}</span>
    <MkTooltip :content="t('dynamicForm.addTitle')" placement="top">
      <el-button text type="primary" @click.stop="handleOpenParamDialog()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </MkTooltip>
  </div>

  <MkTable :data="modelParams" size="small">
    <el-table-column :label="t('dynamicForm.fields.parameter')" prop="field" min-width="130" show-overflow-tooltip />
    <el-table-column :label="t('dynamicForm.fields.displayName')" min-width="130" show-overflow-tooltip>
      <template #default="{ row }">
        <span v-if="row.label && row.label.input_type === 'TooltipLabel'">{{ row.label.label }}</span>
        <span v-else>{{ row.label }}</span>
      </template>
    </el-table-column>
    <el-table-column :label="t('dynamicForm.fields.componentType')" min-width="100">
      <template #default="{ row }">
        <el-tag size="small" type="info">{{ getTypeLabel(row.input_type) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column :label="t('dynamicForm.fields.defaultValue')" prop="default_value" show-overflow-tooltip></el-table-column>
    <el-table-column :label="t('dynamicForm.fields.required')" width="70">
      <template #default="{ row }">
        <el-switch :model-value="row.required ?? false" disabled size="small" />
      </template>
    </el-table-column>
    <el-table-column :label="t('common.fields.actions')" width="100">
      <template #default="{ row, $index }">
        <el-button text type="primary" @click="handleOpenParamDialog(row, $index)">
          <MkIcon name="icon_edit_outlined" />
        </el-button>
        <el-button text type="primary" @click="handleDeleteParam($index)">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </template>
    </el-table-column>
  </MkTable>

  <ModelParamDialog ref="modelParamDialogRef" @submit="handleSubmitParam" />
</template>
