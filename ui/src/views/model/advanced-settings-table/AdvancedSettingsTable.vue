<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DynamicFormField } from '@/api/types'
import type { FormField } from '@/components/mk-dynamics-form'
import { DYNAMIC_FORM_TYPES } from '@/components/mk-dynamics-form'
import ModelParamDialog from './ModelParamDialog.vue'
import { MsgError } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'ModelAdvancedSettings' })

const modelParams = defineModel<DynamicFormField[]>({ required: true })

const currentIndex = ref<number>()
const modelParamDialogRef = useTemplateRef<InstanceType<typeof ModelParamDialog>>('modelParamDialogRef')

function handleOpenParamDialog(field?: DynamicFormField, index?: number) {
  currentIndex.value = index
  modelParamDialogRef.value?.open(field)
}

function getTypeLabel(inputType: string) {
  const definition = DYNAMIC_FORM_TYPES.find(({ value }) => value === inputType)
  return definition ? definition.label : inputType
}

function handleSubmitParam(field: FormField) {
  const label = typeof field.label === 'object' ? { ...field.label, label: field.label.label ?? field.field } : (field.label ?? field.field)
  const modelParam: DynamicFormField = { ...field, label }
  const duplicateField = modelParams.value.some((param, index) => param.field === modelParam.field && index !== currentIndex.value)
  if (duplicateField) {
    MsgError(t('model.parameters.duplicateField', { name: modelParam.field }))
    return
  }

  const modelParamLabel = typeof modelParam.label === 'string' ? modelParam.label : modelParam.label.label
  const duplicateLabel = modelParams.value.some(
    (param, index) => (typeof param.label === 'string' ? param.label : param.label.label) === modelParamLabel && index !== currentIndex.value,
  )
  if (duplicateLabel) {
    MsgError(t('model.parameters.duplicateLabel', { name: modelParamLabel }))
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
    <MkTooltip :content="t('common.parameters.add')" placement="top">
      <el-button text type="primary" @click.stop="handleOpenParamDialog()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </MkTooltip>
  </div>

  <MkTable :data="modelParams" size="small">
    <el-table-column :label="t('dynamicForm.fields.parameter.label')" prop="field" min-width="130" show-overflow-tooltip />
    <el-table-column :label="t('dynamicForm.fields.displayName.label')" min-width="130" show-overflow-tooltip>
      <template #default="{ row }">
        <span v-if="row.label && row.label.input_type === 'TooltipLabel'">{{ row.label.label }}</span>
        <span v-else>{{ row.label }}</span>
      </template>
    </el-table-column>
    <el-table-column :label="t('dynamicForm.fields.inputType.label')" min-width="100">
      <template #default="{ row }">
        <el-tag size="small" type="info">{{ getTypeLabel(row.input_type) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column :label="t('dynamicForm.fields.defaultValue.label')" min-width="90" prop="default_value" show-overflow-tooltip></el-table-column>
    <el-table-column :label="t('dynamicForm.fields.required.columnLabel')" width="90">
      <template #default="{ row }">
        <el-switch :model-value="row.required ?? false" disabled size="small" />
      </template>
    </el-table-column>
    <el-table-column :label="t('common.labels.operation')" width="100">
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
