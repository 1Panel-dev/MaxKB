<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { MsgError } from '@/utils/message'
import type { ChatInputField } from '../../types'
import ConversationVariableDialog from './ConversationVariableDialog.vue'

const inputFields = defineModel<ChatInputField[]>({ required: true })
const fieldDialogRef = useTemplateRef<InstanceType<typeof ConversationVariableDialog>>('fieldDialogRef')

// 表格负责增删和重名检查，校验通过后关闭字段弹窗。
function openDialog(field?: ChatInputField, index?: number) {
  fieldDialogRef.value?.open(field, index)
}

function saveField(data: ChatInputField, index?: number) {
  if (inputFields.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index)) {
    MsgError(`参数已存在：${data.field}`)
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
      <span>会话变量</span>
      <el-button text type="primary" @click="openDialog()"><MkIcon name="icon_add_outlined" /></el-button>
    </div>
    <MkTable class="mt-2 border" v-if="inputFields.length > 0" v-model:data="inputFields" size="small" row-key="field" :max-height="undefined">
      <el-table-column label="参数" prop="field">
        <template #default="{ row }">
          <span :title="row.field" class="block truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column label="显示名称" prop="label">
        <template #default="{ row }">
          <span :title="row.label" class="block truncate">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <el-button text type="primary" @click="openDialog(row, $index)"><MkIcon name="icon_edit_outlined" /></el-button>
          <el-button text type="primary" @click="deleteField($index)"><MkIcon name="icon_delete-trash_outlined" /></el-button>
        </template>
      </el-table-column>
    </MkTable>
  </div>

  <ConversationVariableDialog ref="fieldDialogRef" @submit="saveField" />
</template>
