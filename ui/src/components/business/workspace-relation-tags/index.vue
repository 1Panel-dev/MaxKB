<script setup lang="ts">
import { h, ref } from 'vue'
import { ElScrollbar, type TableTooltipData } from 'element-plus'
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'
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

// 将内层提示挂载在关联浮层内，移入提示时保持外层浮层打开。
const relationContentRef = ref<HTMLDivElement>()

function formatCellValue(value: unknown): string {
  if (Array.isArray(value)) return value.length ? value.join('、') : '-'
  return value === null || value === undefined || value === '' ? '-' : String(value)
}

function formatOverflowTooltip({ cellValue }: TableTooltipData<Record<string, unknown>>) {
  return h(
    ElScrollbar,
    {
      maxHeight: 'min(300px, calc(100vh - 48px))',
      viewClass: 'px-3 py-2',
      // 滚动容器需要明确宽度，避免提示框按内容测量时收缩为空。
      style: { width: '312px', maxWidth: 'calc(100vw - 48px)', overflowWrap: 'anywhere' },
    },
    () => formatCellValue(cellValue),
  )
}
</script>

<template>
  <el-popover placement="bottom" trigger="hover" :width="420" :persistent="false" :show-after="TOOLTIP_SHOW_DELAY" :disabled="!data.length">
    <template #reference>
      <MkTagGroup :tags="tags" popover-disabled :class="{ 'cursor-pointer': data.length }" />
    </template>
    <div ref="relationContentRef" class="p-6">
      <MkTable :data="data" max-height="300" size="small">
        <template v-for="column in columns" :key="column.prop">
          <el-table-column
            :label="column.label"
            :prop="column.prop"
            :show-overflow-tooltip="{
              appendTo: relationContentRef,
              placement: 'bottom',
              popperOptions: { strategy: 'absolute' },
              popperStyle: { padding: '0' },
              enterable: true,
              hideAfter: 200,
            }"
            :tooltip-formatter="formatOverflowTooltip"
          >
            <template #default="{ row }">
              {{ formatCellValue(row[column.prop]) }}
            </template>
          </el-table-column>
        </template>
      </MkTable>
    </div>
  </el-popover>
</template>
