<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { ToolInitField } from '@/api/types'
import InitFieldDialog from './InitFieldDialog.vue'

defineOptions({ name: 'InitFieldTable' })

const initFields = defineModel<ToolInitField[]>({ required: true })
const currentIndex = ref<number>()

const initFieldDialogRef =
  useTemplateRef<InstanceType<typeof InitFieldDialog>>('initFieldDialogRef')

const initFieldTypeOptions = [
  { label: '文本框', value: 'TextInput' },
  { label: '密码框', value: 'PasswordInput' },
  { label: 'JSON 输入框', value: 'JsonInput' },
  { label: '开关', value: 'SwitchInput' },
]

function handleOpenInitField(field?: ToolInitField, index?: number) {
  currentIndex.value = index
  initFieldDialogRef.value?.open(field)
}

function handleAddInitField(field: ToolInitField) {
  if (currentIndex.value === undefined) {
    initFields.value.push(field)
    return
  }
  initFields.value.splice(currentIndex.value, 1, field)
}

function handleDeleteInitField(index: number) {
  initFields.value.splice(index, 1)
}
</script>

<template>
  <section>
    <div class="mb-4 flex-between">
      <h4 class="mk-title-decoration">启动参数</h4>
      <el-button link type="primary" @click="handleOpenInitField()">
        <MkIcon name="icon_add_outlined" />
        <span>添加</span>
      </el-button>
    </div>
    <MkTable :data="initFields" size="small">
      <el-table-column label="参数" prop="field" min-width="140" />
      <el-table-column label="组件类型" min-width="120">
        <template #default="{ row }">
          <el-tag size="small" type="info">
            {{ initFieldTypeOptions.find((option) => option.value === row.input_type)?.label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="必填" width="80">
        <template #default="{ row }">
          <el-switch v-model="row.required" size="small" disabled />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row, $index }">
          <el-button text type="primary" @click="handleOpenInitField(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <el-button text type="primary" @click="handleDeleteInitField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </MkTable>
    <InitFieldDialog ref="initFieldDialogRef" @refresh="handleAddInitField" />
  </section>
</template>
