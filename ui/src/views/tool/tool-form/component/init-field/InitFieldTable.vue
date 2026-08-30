<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { DynamicFormField } from '@/api/types'
import { dynamicFormTypeOptions, type FormField } from '@/components/mk-dynamics-form'
import InitFieldDialog from './InitFieldDialog.vue'

defineOptions({ name: 'InitFieldTable' })

const initFields = defineModel<DynamicFormField[]>({ required: true })
const currentIndex = ref<number>()

const initFieldDialogRef = useTemplateRef<InstanceType<typeof InitFieldDialog>>('initFieldDialogRef')

function handleOpenInitField(field?: DynamicFormField, index?: number) {
  currentIndex.value = index
  initFieldDialogRef.value?.open(field)
}

function handleAddInitField(field: FormField) {
  const label = typeof field.label === 'object' ? { ...field.label, label: field.label.label ?? field.field } : (field.label ?? field.field)
  const initField: DynamicFormField = { ...field, label }

  if (currentIndex.value === undefined) {
    initFields.value.push(initField)
    return
  }
  initFields.value.splice(currentIndex.value, 1, initField)
}

function handleDeleteInitField(index: number) {
  initFields.value.splice(index, 1)
}

function getTypeLabel(inputType: string) {
  return dynamicFormTypeOptions.find((option) => option.value === inputType)?.label ?? inputType
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
      <el-table-column label="显示名称" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.label && row.label.input_type === 'TooltipLabel'">{{ row.label.label }}</span>
          <span v-else>{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="组件类型" min-width="100">
        <template #default="{ row }">
          <el-tag size="small" type="info">
            {{ getTypeLabel(row.input_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="默认值" prop="default_value" show-overflow-tooltip> </el-table-column>
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
    <InitFieldDialog ref="initFieldDialogRef" @submit="handleAddInitField" />
  </section>
</template>
