<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { DynamicFormField } from '@/api/types'
import { dynamicFormTypeOptions, type FormField } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'
import ModelParamDialog from './ModelParamDialog.vue'

defineOptions({ name: 'ModelAdvancedSettings' })

const modelParams = defineModel<DynamicFormField[]>({ required: true })

const currentIndex = ref<number>()
const modelParamDialogRef = useTemplateRef<InstanceType<typeof ModelParamDialog>>('modelParamDialogRef')

function handleOpenParamDialog(field?: DynamicFormField, index?: number) {
  currentIndex.value = index
  modelParamDialogRef.value?.open(field)
}

function getTypeLabel(inputType: string) {
  return dynamicFormTypeOptions.find((option) => option.value === inputType)?.label ?? inputType
}

function handleSubmitParam(field: FormField) {
  const label = typeof field.label === 'object' ? { ...field.label, label: field.label.label ?? field.field } : (field.label ?? field.field)
  const modelParam: DynamicFormField = { ...field, label }
  const duplicateField = modelParams.value.some((param, index) => param.field === modelParam.field && index !== currentIndex.value)
  if (duplicateField) {
    MsgError(`参数“${modelParam.field}”已存在`)
    return
  }

  const modelParamLabel = typeof modelParam.label === 'string' ? modelParam.label : modelParam.label.label
  const duplicateLabel = modelParams.value.some(
    (param, index) => (typeof param.label === 'string' ? param.label : param.label.label) === modelParamLabel && index !== currentIndex.value,
  )
  if (duplicateLabel) {
    MsgError(`显示名称“${modelParamLabel}”已存在`)
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
    <span>模型参数</span>
    <el-tooltip content="添加参数" placement="top">
      <el-button text type="primary" @click.stop="handleOpenParamDialog()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </el-tooltip>
  </div>

  <MkTable :data="modelParams" size="small">
    <el-table-column label="参数" prop="field" min-width="130" show-overflow-tooltip />
    <el-table-column label="显示名称" min-width="130" show-overflow-tooltip>
      <template #default="{ row }">
        <span v-if="row.label && row.label.input_type === 'TooltipLabel'">{{ row.label.label }}</span>
        <span v-else>{{ row.label }}</span>
      </template>
    </el-table-column>
    <el-table-column label="组件类型" min-width="100">
      <template #default="{ row }">
        <el-tag size="small" type="info">{{ getTypeLabel(row.input_type) }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="默认值" prop="default_value" show-overflow-tooltip> </el-table-column>
    <el-table-column label="必填" width="70">
      <template #default="{ row }">
        <el-switch :model-value="row.required ?? false" disabled size="small" />
      </template>
    </el-table-column>
    <el-table-column label="操作" width="100">
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
