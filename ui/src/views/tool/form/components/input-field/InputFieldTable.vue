<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { ToolInputField } from '@/api/types'
import InputFieldDialog from './InputFieldDialog.vue'

defineOptions({ name: 'InputFieldTable' })

const inputFields = defineModel<ToolInputField[]>({ required: true })
const currentIndex = ref<number>()

const inputFieldDialogRef =
  useTemplateRef<InstanceType<typeof InputFieldDialog>>('inputFieldDialogRef')

function handleOpenInputField(field?: ToolInputField, index?: number) {
  currentIndex.value = index
  inputFieldDialogRef.value?.open(field)
}

function handleAddInputField(field: ToolInputField) {
  if (currentIndex.value === undefined) {
    inputFields.value.push(field)
    return
  }
  inputFields.value.splice(currentIndex.value, 1, field)
}

function handleDeleteInputField(index: number) {
  inputFields.value.splice(index, 1)
}
</script>

<template>
  <section>
    <div class="mb-4 flex-between">
      <div class="flex items-center gap-2">
        <h4 class="mk-title-decoration">输入参数</h4>
        <span class="text-N600">使用工具时显示</span>
      </div>
      <el-button link type="primary" @click="handleOpenInputField()">
        <MkIcon name="icon_add_outlined" />
        <span>添加</span>
      </el-button>
    </div>
    <el-table :data="inputFields">
      <el-table-column label="参数" prop="name" min-width="140" />
      <el-table-column label="数据类型" prop="type" min-width="100">
        <template #default="{ row }">
          <el-tag size="small" type="info" class="info-tag">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="来源" min-width="100">
        <template #default="{ row }">{{
          row.source === 'custom' ? '自定义' : '引用参数'
        }}</template>
      </el-table-column>
      <el-table-column label="必填" width="80">
        <template #default="{ row }">
          <el-switch v-model="row.is_required" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row, $index }">
          <el-button text type="primary" @click="handleOpenInputField(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <el-button text type="primary" @click="handleDeleteInputField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <InputFieldDialog ref="inputFieldDialogRef" @refresh="handleAddInputField" />
  </section>
</template>
