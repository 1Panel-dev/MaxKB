<script setup lang="ts" generic="T">
import { computed, onBeforeUnmount, onMounted, ref, type VNode } from 'vue'
import type { TableInstance } from 'element-plus'
import LayoutBatchFooter from '../mk-view-layout/LayoutBatchFooter.vue'
import { useSortable, type SortableChange } from '@/utils/use-sortable'
import { get } from 'lodash'

defineOptions({ name: 'MkTable', inheritAttrs: false })

const DEFAULT_PAGE_SIZES = [10, 20, 50, 100]

interface PaginationConfig {
  currentPage: number
  pageSize: number
  pageSizes?: number[]
  total: number
}

const props = withDefaults(
  defineProps<{
    data?: T[]
    maxTableHeight?: number
    paginationConfig?: PaginationConfig
    resizable?: boolean // 非指定表格禁止开启
    size?: 'small'
    rowKey?: string | ((row: T) => string | number)
    sortable?: boolean
  }>(),
  { data: () => [], maxTableHeight: 250, resizable: false, rowKey: 'id', sortable: false },
)

const emit = defineEmits<{
  'current-change': [currentPage: number]
  'selection-change': [selection: unknown[]]
  'size-change': [pageSize: number]
  'update:paginationConfig': [paginationConfig: PaginationConfig]
  'update:data': [data: T[]]
  'sort-change': [change: SortableChange<T>]
}>()

const tableRef = ref<TableInstance>()

defineSlots<{
  default?: () => VNode[]
  'body-prepend'?: () => VNode[]
  'footer-batch-actions'?: () => VNode[]
}>()

/** 行排序：只处理当前传入的平面数据，保持显示顺序与数组索引一致。 */
const sortableRows = computed({
  get: () => props.data,
  set: (data: T[]) => emit('update:data', data),
})
const canSortRows = computed(() => {
  if (!props.sortable || props.data.length < 2) return false
  const states = tableRef.value?.store.states
  if (!states || states.sortOrder.value || states.expandRows.value.length || Object.keys(states.treeData.value).length) return false
  if (Object.values(states.filters.value).some((values) => values.length > 0)) return false
  const keys = props.data.map((row) => (typeof props.rowKey === 'function' ? props.rowKey(row) : get(row, props.rowKey)))
  if (keys.some((key) => typeof key !== 'string' && typeof key !== 'number') || new Set(keys).size !== keys.length) return false
  const displayedRows = states.data.value as T[]
  return displayedRows.length === props.data.length && displayedRows.every((row, index) => row === props.data[index])
})
useSortable(
  () => (props.sortable ? (tableRef.value?.$el.querySelector('.el-table__body-wrapper tbody') as HTMLElement | null) : null),
  sortableRows,
  () => ({
    disabled: !canSortRows.value,
    draggable: '> tr.el-table__row',
    onReorder: (change) => emit('sort-change', change),
  }),
)

const paginationPageSizes = computed(() => props.paginationConfig?.pageSizes ?? DEFAULT_PAGE_SIZES)

/** 表格高度 */
const tableHeight = ref(window.innerHeight - props.maxTableHeight)
function updateTableHeight() {
  tableHeight.value = props.paginationConfig ? window.innerHeight - props.maxTableHeight : window.innerHeight - props.maxTableHeight + 50
}

/** 选择操作栏 */
const selectedRows = ref<unknown[]>([])
const isAllRowsSelected = computed(() => tableRef.value?.store.states.isAllSelected.value ?? false)

function handleSelectionChange(selection: unknown[]) {
  selectedRows.value = selection
  emit('selection-change', selection)
}

function handleToggleAllSelection() {
  tableRef.value?.toggleAllSelection()
}

function clearSelection() {
  tableRef.value?.clearSelection()
  selectedRows.value = []
}

/** 分页 */
function handleCurrentPageChange(currentPage: number) {
  if (!props.paginationConfig) {
    return
  }

  emit('update:paginationConfig', { ...props.paginationConfig, currentPage })
  emit('current-change', currentPage)
}

function handlePageSizeChange(pageSize: number) {
  if (!props.paginationConfig) {
    return
  }

  emit('update:paginationConfig', { ...props.paginationConfig, currentPage: 1, pageSize })
  emit('size-change', pageSize)
}

onMounted(() => {
  updateTableHeight()
  window.addEventListener('resize', updateTableHeight)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateTableHeight)
})

defineExpose({ clearSelection, tableRef })
</script>

<template>
  <div class="mk-table relative flex-column w-full min-h-0 flex-1">
    <el-table
      ref="tableRef"
      :class="{
        'mk-table__resizable--borderless': props.resizable,
        'mk-table__body-prepend': !!$slots['body-prepend'],
        small: props.size === 'small',
      }"
      :data="props.data"
      :max-height="tableHeight"
      :row-key="props.rowKey"
      v-bind="$attrs"
      :border="props.resizable"
      @selection-change="handleSelectionChange"
    >
      <slot />
      <template v-if="$slots['body-prepend']" #append>
        <slot name="body-prepend" />
      </template>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="props.paginationConfig">
      <el-pagination
        background
        :current-page="props.paginationConfig.currentPage"
        layout="total, prev, pager, next, sizes"
        :page-size="props.paginationConfig.pageSize"
        :page-sizes="paginationPageSizes"
        :total="props.paginationConfig.total"
        @current-change="handleCurrentPageChange"
        @size-change="handlePageSizeChange"
        :pager-count="5"
      />
    </div>

    <LayoutBatchFooter
      v-if="selectedRows.length > 0 && $slots['footer-batch-actions']"
      :all-selected="isAllRowsSelected"
      :selected-count="selectedRows.length"
      :total="props.data.length"
      class="sticky -mx-6 -mb-6 bottom-0 z-10 mt-auto"
      @cancel="clearSelection"
      @select-all="handleToggleAllSelection"
    >
      <slot name="footer-batch-actions" />
    </LayoutBatchFooter>
  </div>
</template>

<style scoped lang="scss">
/* 表体顶部插槽：自然占位并固定在滚动区域顶部，不影响嵌套表格。 */
:deep(.mk-table__body-prepend) {
  > .el-table__inner-wrapper > .el-table__body-wrapper {
    container-type: inline-size;

    > .el-scrollbar > .el-scrollbar__wrap > .el-scrollbar__view {
      display: flex !important;
      flex-direction: column;
      min-width: 100%;
      width: max-content;

      > .el-table__append-wrapper {
        background: var(--el-bg-color);
        border-bottom: var(--el-table-border);
        cursor: pointer;
        flex-shrink: 0;
        left: 0;
        order: -1;
        position: sticky;
        top: 0;
        width: 100cqw;
        z-index: 3;

        &:hover {
          background: var(--el-table-row-hover-bg-color);
        }
      }

      > .el-table__body,
      > .el-table__empty-block {
        flex-shrink: 0;
      }
    }
  }
}

:deep(.mk-table__resizable--borderless) {
  border: none !important;

  &,
  &::after,
  &::before,
  td,
  th {
    border-right: none !important;
  }

  .el-table__border-left-patch {
    display: none;
  }

  .el-table__header-wrapper:hover th.el-table__cell:not(:last-child)::after {
    background-color: var(--mk-N300);
    content: '';
    height: 22px;
    pointer-events: none;
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 2px;
    z-index: 1;
  }
  .el-table__column-resize-proxy {
    border-left: 2px solid var(--el-color-primary);
  }

  thead th {
    border-bottom: none !important;
  }
}
</style>
