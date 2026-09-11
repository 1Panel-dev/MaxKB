<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { MsgError } from '@/utils/message'
import type { ToolOutputField, ToolFieldConfig } from '../../types'
import OutputFieldFormDialog from './OutputFieldFormDialog.vue'
import TitleSettingDialog from './TitleSettingDialog.vue'

const fields = defineModel<ToolOutputField[]>({ required: true })
const config = defineModel<ToolFieldConfig>('config', { required: true })
const fieldDialogRef = useTemplateRef<InstanceType<typeof OutputFieldFormDialog>>('fieldDialogRef')
const titleDialogRef = useTemplateRef<InstanceType<typeof TitleSettingDialog>>('titleDialogRef')

// 表格只维护列表和重名检查，节点入口统一同步变量。
function saveField(data: ToolOutputField, index?: number) {
  if (fields.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index)) {
    MsgError(`参数已存在：${data.field}`)
    return
  }
  const nextFields = cloneDeep(fields.value)
  if (index === undefined) nextFields.push(cloneDeep(data))
  else nextFields.splice(index, 1, cloneDeep(data))
  fields.value = nextFields
  fieldDialogRef.value?.close()
}

function deleteField(index: number) {
  fields.value = cloneDeep(fields.value.filter((_, fieldIndex) => fieldIndex !== index))
}

function saveTitle(data: ToolFieldConfig) {
  config.value = cloneDeep(data)
  titleDialogRef.value?.close()
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between gap-2">
      <span class="min-w-0 truncate" :title="config.title">{{ config.title }}</span>
      <div class="flex shrink-0 items-center">
        <!-- 设置标题 -->
        <el-button text type="primary" @click="titleDialogRef?.open(config)"><MkIcon name="icon_setting" /></el-button>
        <!-- 添加参数 -->
        <el-button text type="primary" @click="fieldDialogRef?.open()"><MkIcon name="icon_add_outlined" /></el-button>
      </div>
    </div>
    <MkTable v-if="fields.length" v-model:data="fields" size="small" row-key="field" class="mt-2 border" :max-height="undefined">
      <el-table-column prop="field" label="参数" min-width="100">
        <template #default="{ row }">
          <span class="block truncate" :title="row.field">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="显示名称" min-width="100">
        <template #default="{ row }">
          <span class="block truncate" :title="row.label">{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <!-- 编辑参数 -->
          <el-button text type="primary" @click="fieldDialogRef?.open(row, $index)"><MkIcon name="icon_edit_outlined" /></el-button>
          <!-- 删除参数 -->
          <el-button text type="primary" @click="deleteField($index)"><MkIcon name="icon_delete-trash_outlined" /></el-button>
        </template>
      </el-table-column>
    </MkTable>
  </div>
  <OutputFieldFormDialog ref="fieldDialogRef" @submit="saveField" />
  <TitleSettingDialog ref="titleDialogRef" @submit="saveTitle" />
</template>
