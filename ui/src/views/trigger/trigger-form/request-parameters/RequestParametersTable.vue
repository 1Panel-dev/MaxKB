<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { TriggerBodyField } from '@/api/types'
import RequestParameterDialog from './RequestParameterDialog.vue'

const body = defineModel<TriggerBodyField[] | undefined>({ required: true })
const fields = computed({
  get: () => body.value ?? [],
  set: (value: TriggerBodyField[]) => {
    body.value = value
  },
})
const dialogRef = useTemplateRef<InstanceType<typeof RequestParameterDialog>>('dialogRef')

function saveField(field: TriggerBodyField, index?: number) {
  const updatedFields = cloneDeep(fields.value)
  if (index === undefined) updatedFields.push(cloneDeep(field))
  else updatedFields.splice(index, 1, cloneDeep(field))
  fields.value = updatedFields
  dialogRef.value?.close()
}

function removeField(index: number) {
  fields.value = fields.value.filter((_, fieldIndex) => fieldIndex !== index)
}
function updateRequired(index: number, required: boolean) {
  fields.value = fields.value.map((field, fieldIndex) => (fieldIndex === index ? { ...field, required } : field))
}
function formatFieldType(type: TriggerBodyField['type']) {
  return type.charAt(0).toUpperCase() + type.slice(1)
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between mt-4">
      <p>请求参数</p>
      <!-- 添加请求参数 -->
      <el-button text type="primary" title="添加请求参数" @click="dialogRef?.open()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </div>
    <MkTable v-if="fields.length > 0" :data="fields" row-key="field" size="small" class="mt-2 border" :max-height="undefined">
      <el-table-column label="参数">
        <template #default="{ row }">
          <span class="block truncate" :title="row.field">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column label="数据类型" width="100">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ formatFieldType(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="110" >
        <template #default="{ row }">
          <span class="block truncate" :title="row.desc || '-'">{{ row.desc || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="必填" width="64">
        <template #default="{ row, $index }">
          <!-- 切换参数必填状态 -->
          <el-switch :model-value="Boolean(row.required)" size="small" @change="updateRequired($index, Boolean($event))" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <!-- 编辑请求参数 -->
          <el-button text type="primary" title="编辑" @click="dialogRef?.open(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <!-- 删除请求参数 -->
          <el-button text type="primary" title="删除" @click="removeField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </MkTable>
    <RequestParameterDialog ref="dialogRef" :fields="fields" @submit="saveField" />
  </div>
</template>
