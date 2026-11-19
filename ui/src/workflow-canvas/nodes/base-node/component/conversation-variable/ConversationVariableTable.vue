<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ChatInputField } from '../../types'
import ConversationVariableDialog from './ConversationVariableDialog.vue'
import { MsgError } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

const inputFields = defineModel<ChatInputField[]>({ required: true })
const fieldDialogRef = useTemplateRef<InstanceType<typeof ConversationVariableDialog>>('fieldDialogRef')

// 表格负责增删和重名检查，校验通过后关闭字段弹窗。
function openDialog(field?: ChatInputField, index?: number) {
  fieldDialogRef.value?.open(field, index)
}

function saveField(data: ChatInputField, index?: number) {
  if (inputFields.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index)) {
    MsgError(`${t('workflow.parameters.duplicateMessage')}：${data.field}`)
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
      <span>{{ t('workflow.conversationVariables.title') }}</span>
      <!-- 添加会话变量 -->
      <el-button text type="primary" @click="openDialog()"><MkIcon name="icon_add_outlined" /></el-button>
    </div>
    <MkTable class="mt-2 border" v-if="inputFields.length > 0" v-model:data="inputFields" size="small" row-key="field" :max-height="undefined">
      <el-table-column :label="t('dynamicForm.fields.parameter.label')" prop="field">
        <template #default="{ row }">
          <span :title="row.field" class="block truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('dynamicForm.fields.displayName.label')" prop="label">
        <template #default="{ row }">
          <span :title="row.label" class="block truncate">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.labels.operation')" width="80">
        <template #default="{ row, $index }">
          <!-- 编辑会话变量 -->
          <el-button text type="primary" @click="openDialog(row, $index)"><MkIcon name="icon_edit_outlined" /></el-button>
          <!-- 删除会话变量 -->
          <el-button text type="primary" @click="deleteField($index)"><MkIcon name="icon_delete-trash_outlined" /></el-button>
        </template>
      </el-table-column>
    </MkTable>
  </div>

  <ConversationVariableDialog ref="fieldDialogRef" @submit="saveField" />
</template>
