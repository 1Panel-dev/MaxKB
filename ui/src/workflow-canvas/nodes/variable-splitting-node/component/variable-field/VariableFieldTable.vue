<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'

import VariableFieldDialog from './VariableFieldDialog.vue'
import type { VariableField } from './types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowVariableSplittingFieldTable' })

const variableList = defineModel<VariableField[]>({ required: true })
const variableFieldDialogRef = useTemplateRef<InstanceType<typeof VariableFieldDialog>>('variableFieldDialogRef')

function openFieldDialog(data?: VariableField, index?: number) {
  variableFieldDialogRef.value?.open(data, index)
}

function deleteField(index: number) {
  variableList.value = cloneDeep(variableList.value.filter((_, fieldIndex) => fieldIndex !== index))
}

function saveField(data: VariableField, index?: number) {
  if (variableList.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index)) {
    MsgError(`变量 "${data.field}" 已存在`)
    return
  }

  const fields = cloneDeep(variableList.value)
  if (index === undefined) {
    fields.push(cloneDeep(data))
  } else {
    fields.splice(index, 1, cloneDeep(data))
  }
  variableList.value = fields
  variableFieldDialogRef.value?.close()
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between mb-2">
      <span class="mk-required">拆分变量</span>
      <el-button text type="primary" @click="openFieldDialog()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </div>

    <MkTable v-if="variableList.length" size="small" class="border" :data="variableList" row-key="field">
      <el-table-column prop="field" label="变量">
        <template #default="{ row }">
          <span :title="row.field" class="block truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="显示名称">
        <template #default="{ row }">
          <span :title="row.label" class="block truncate">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <el-button text type="primary" @click="openFieldDialog(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <el-button text type="primary" @click="deleteField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </MkTable>

    <VariableFieldDialog ref="variableFieldDialogRef" @submit="saveField" />
  </div>
</template>
