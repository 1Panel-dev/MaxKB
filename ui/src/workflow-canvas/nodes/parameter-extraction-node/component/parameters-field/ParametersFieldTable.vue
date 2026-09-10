<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import ParametersFieldDialog from './ParametersFieldDialog.vue'
import type { ParameterField } from './types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowParameterExtractionFieldTable' })

const parameterList = defineModel<ParameterField[]>({ required: true })
const parametersFieldDialogRef = useTemplateRef<InstanceType<typeof ParametersFieldDialog>>('parametersFieldDialogRef')

function openFieldDialog(data?: ParameterField, index?: number) {
  parametersFieldDialogRef.value?.open(data, index)
}

function deleteField(index: number) {
  parameterList.value = cloneDeep(parameterList.value.filter((_, fieldIndex) => fieldIndex !== index))
}

function saveField(data: ParameterField, index?: number) {
  if (parameterList.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index)) {
    MsgError(`参数 "${data.field}" 已存在`)
    return
  }

  const fields = cloneDeep(parameterList.value)
  if (index === undefined) {
    fields.push(cloneDeep(data))
  } else {
    fields.splice(index, 1, cloneDeep(data))
  }
  parameterList.value = fields
  parametersFieldDialogRef.value?.close()
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between mb-2">
      <span class="mk-required">提取参数</span>
      <el-button text type="primary" @click="openFieldDialog()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </div>

    <MkTable v-if="parameterList.length" size="small" class="border" :data="parameterList" row-key="field">
      <el-table-column prop="field" label="参数">
        <template #default="{ row }">
          <span :title="row.field" class="block truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="显示名称">
        <template #default="{ row }">
          <span :title="row.label" class="block truncate">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="参数类型" width="90">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ row.parameter_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <!-- 编辑 -->
          <el-button text type="primary" @click="openFieldDialog(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <!-- 删除 -->
          <el-button text type="primary" @click="deleteField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </MkTable>

    <ParametersFieldDialog ref="parametersFieldDialogRef" @submit="saveField" />
  </div>
</template>
