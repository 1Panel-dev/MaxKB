<script setup lang="ts">
defineOptions({ name: 'WorkspaceRelationTags' })

interface RelationColumn {
  prop: string
  label: string
}

defineProps<{
  tags?: string[]
  data: Record<string, unknown>[]
  columns: RelationColumn[]
}>()

function formatCellValue(value: unknown): string {
  if (Array.isArray(value)) return value.length ? value.join('、') : '-'
  return value === null || value === undefined || value === '' ? '-' : String(value)
}
</script>

<template>
  <el-popover placement="bottom" trigger="hover" :width="420" :persistent="false" :show-after="300" :disabled="!data.length">
    <template #reference>
      <MkTagGroup :tags="tags" popover-disabled :class="{ 'cursor-pointer': data.length }" />
    </template>
    <div class="p-6">
      <MkTable :data="data" max-height="300" size="small">
        <template v-for="column in columns" :key="column.prop">
          <el-table-column :label="column.label" :prop="column.prop" :show-overflow-tooltip="{ appendTo: 'body' }">
            <template #default="{ row }">
              {{ formatCellValue(row[column.prop]) }}
            </template>
          </el-table-column>
        </template>
      </MkTable>
    </div>
  </el-popover>
</template>
