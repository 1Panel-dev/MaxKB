<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormField } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'
import type { ApiInputField } from '../../types'
import ApiParameterDialog from './ApiParameterDialog.vue'

const props = defineProps<{ userFields: FormField[] }>()
const inputFields = defineModel<ApiInputField[]>({ required: true })
const fieldDialogRef = useTemplateRef<InstanceType<typeof ApiParameterDialog>>('fieldDialogRef')

// 表格负责增删和重名检查，校验通过后关闭字段弹窗。
function openDialog(field?: ApiInputField, index?: number) {
  fieldDialogRef.value?.open(field, index)
}

function saveField(data: ApiInputField, index?: number) {
  if (
    inputFields.value.some((field, fieldIndex) => field.variable === data.variable && fieldIndex !== index) ||
    props.userFields.some(({ field }) => field === data.variable)
  ) {
    MsgError(`参数已存在：${data.variable}`)
    return
  }
  const fields = cloneDeep(inputFields.value)
  if (index === undefined) fields.push(cloneDeep(data))
  else fields.splice(index, 1, cloneDeep(data))
  inputFields.value = fields
  fieldDialogRef.value?.close()
}

function deleteField(index: number) {
  inputFields.value = cloneDeep(inputFields.value.filter((_, fieldIndex) => fieldIndex !== index))
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between">
      <span>接口传参</span>
      <el-button text type="primary" @click="openDialog()"><MkIcon name="icon_add_outlined" /></el-button>
    </div>
    <MkTable
      class="mt-2 border"
      v-if="inputFields.length"
      :datav-model:data="inputFields"
      sortable
      size="small"
      row-key="variable"
      :max-height="undefined"
    >
      <el-table-column label="参数" prop="variable" min-width="120" show-overflow-tooltip />
      <el-table-column label="描述" prop="desc" min-width="120" show-overflow-tooltip />
      <el-table-column label="默认值" prop="default_value" min-width="100" show-overflow-tooltip />
      <el-table-column label="必填" width="55">
        <template #default="{ row }"><el-switch :model-value="Boolean(row.is_required)" disabled size="small" /></template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <el-button text type="primary" aria-label="编辑" @click="openDialog(row, $index)"><MkIcon name="icon_edit_outlined" /></el-button>
          <el-button text type="primary" aria-label="删除" @click="deleteField($index)"><MkIcon name="icon_delete-trash_outlined" /></el-button>
        </template>
      </el-table-column>
    </MkTable>
  </div>

  <ApiParameterDialog ref="fieldDialogRef" @submit="saveField" />
</template>
