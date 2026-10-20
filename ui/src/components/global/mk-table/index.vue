<script setup lang="ts" generic="T extends object">
import { cloneVNode, computed, Fragment, h, isVNode, nextTick, onBeforeUnmount, onMounted, ref, type VNode } from 'vue'
import { ElTableColumn, type TableColumnCtx, type TableInstance } from 'element-plus'
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
    /** 同组记录联动选择；不传时保持逐行选择。 */
    selectionGroupKey?: string | ((row: T) => string | number | null | undefined)
    sortable?: boolean
  }>(),
  { data: () => [], maxTableHeight: 250, resizable: false, rowKey: 'id', sortable: false },
)

const emit = defineEmits<{
  'current-change': [currentPage: number]
  'selection-change': [selection: unknown[]]
  'row-click': [row: T, column: TableColumnCtx<T> | null, event: PointerEvent]
  'size-change': [pageSize: number]
  'update:paginationConfig': [paginationConfig: PaginationConfig]
  'update:data': [data: T[]]
  'row-sort-change': [change: SortableChange<T>]
}>()

const tableRef = ref<TableInstance>()

/** 列宽拖拽：按当前表头的单行内容限制拖拽线，保留原生拖拽与事件。 */
let columnResize: { proxy: HTMLElement; minLeft: number } | undefined

function clampColumnResize() {
  if (!props.resizable || !columnResize) return
  const { proxy, minLeft } = columnResize
  proxy.style.left = `${Math.max(minLeft, Number.parseFloat(proxy.style.left))}px`
}

function clearColumnResize() {
  columnResize = undefined
  document.removeEventListener('mousemove', clampColumnResize)
  document.removeEventListener('mouseup', finishColumnResize, true)
}

function finishColumnResize() {
  // 在 Element Plus 读取拖拽线并发出 header-dragend 前完成最后一次限制。
  clampColumnResize()
  clearColumnResize()
}

function handleColumnResizeStart(event: MouseEvent) {
  const table = tableRef.value?.$el as HTMLElement | undefined
  const header = event.target instanceof Element ? event.target.closest<HTMLElement>('th.noclick') : null
  if (!props.resizable || !table || !header || header.closest('.el-table') !== table) return
  const cell = header.querySelector<HTMLElement>(':scope > .cell')
  const proxy = table.querySelector<HTMLElement>(':scope > .el-table__column-resize-proxy')
  if (!cell || !proxy) return

  // 原位测量保留继承字体、图标、按钮与间距；同步还原，不改变实际表头布局。
  const previousStyle = cell.style.cssText
  cell.style.width = 'max-content'
  cell.style.minWidth = '0'
  cell.style.maxWidth = 'none'
  const contentWidth = cell.getBoundingClientRect().width
  cell.style.cssText = previousStyle
  const headerStyle = getComputedStyle(header)
  const outerWidth = ['padding-left', 'padding-right', 'border-left-width', 'border-right-width'].reduce(
    (width, property) => width + (Number.parseFloat(headerStyle.getPropertyValue(property)) || 0),
    0,
  )

  clearColumnResize()
  columnResize = {
    proxy,
    minLeft: Math.ceil(header.getBoundingClientRect().left - table.getBoundingClientRect().left + Math.max(30, Math.ceil(contentWidth + outerWidth))),
  }
  clampColumnResize()
  // 冒泡到表格后注册，确保每次在 Element Plus 更新拖拽线之后执行。
  document.addEventListener('mousemove', clampColumnResize)
  document.addEventListener('mouseup', finishColumnResize, true)
}

/** 行内名称编辑：失焦的这次点击不再触发行点击，下一次点击恢复。 */
let nameEditingOnPointerDown = false

function handlePointerDown(event: PointerEvent) {
  const editor = document.activeElement instanceof HTMLElement ? document.activeElement.closest('[data-mk-edit-name-editing]') : null
  nameEditingOnPointerDown = !!editor && event.currentTarget instanceof HTMLElement && event.currentTarget.contains(editor)
}

function handleRowClick(row: T, column: TableColumnCtx<T> | null, event: PointerEvent) {
  const skipRowClick = nameEditingOnPointerDown
  nameEditingOnPointerDown = false
  if (skipRowClick && event.detail > 0) return
  emit('row-click', row, column, event)
}

const slots = defineSlots<{
  default?: () => VNode[]
  'body-prepend'?: () => VNode[]
  'footer-batch-actions'?: () => VNode[]
}>()

/** 表头排序统一交给调用方；在 Element Plus 排序前转换，避免重排当前页。 */
function normalizeColumn(column: VNode): VNode {
  if (column.type === Fragment && Array.isArray(column.children)) {
    return h(
      Fragment,
      column.props,
      column.children.map((child) => (isVNode(child) ? normalizeColumn(child) : child)),
    )
  }
  if (column.type !== ElTableColumn) return column

  const sortable = column.props?.sortable
  const normalizedColumn = cloneVNode(column, sortable === true || sortable === '' ? { sortable: 'custom' } : undefined)
  const columnSlots = column.children
  if (columnSlots && !Array.isArray(columnSlots) && typeof columnSlots === 'object' && typeof columnSlots.default === 'function') {
    const defaultSlot = columnSlots.default
    normalizedColumn.children = {
      ...columnSlots,
      default: (...args: unknown[]) => defaultSlot(...args).map(normalizeColumn),
    }
  }
  return normalizedColumn
}

const TableColumns = () => slots.default?.().map(normalizeColumn)

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
    onReorder: (change) => emit('row-sort-change', change),
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
let groupSelectionPending = false

function getSelectionGroupKey(row: T): unknown {
  const key = props.selectionGroupKey
  return typeof key === 'function' ? key(row) : key ? get(row, key) : undefined
}

function handleSelect(selection: T[], row: T) {
  const groupKey = getSelectionGroupKey(row)
  if ((typeof groupKey !== 'string' && typeof groupKey !== 'number') || !tableRef.value) return

  // 等整组勾选完成后再更新选择结果，保证已选数量和批量操作包含组内所有记录。
  if (!groupSelectionPending) {
    groupSelectionPending = true
    nextTick(() => {
      groupSelectionPending = false
      if (tableRef.value) handleSelectionChange(tableRef.value.getSelectionRows())
    })
  }

  const checked = selection.includes(row)
  props.data.forEach((groupRow) => {
    if (getSelectionGroupKey(groupRow) === groupKey) {
      tableRef.value?.toggleRowSelection(groupRow, checked, false)
    }
  })
}

function handleSelectionChange(selection: unknown[]) {
  if (groupSelectionPending) return
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

  clearSelection()
  emit('update:paginationConfig', { ...props.paginationConfig, currentPage })
  emit('current-change', currentPage)
}

function handlePageSizeChange(pageSize: number) {
  if (!props.paginationConfig) {
    return
  }

  clearSelection()
  emit('update:paginationConfig', { ...props.paginationConfig, currentPage: 1, pageSize })
  emit('size-change', pageSize)
}

onMounted(() => {
  updateTableHeight()
  window.addEventListener('resize', updateTableHeight)
})

onBeforeUnmount(() => {
  clearColumnResize()
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
      @select="handleSelect"
      @selection-change="handleSelectionChange"
      @pointerdown.capture="handlePointerDown"
      @mousedown="handleColumnResizeStart"
      @row-click="handleRowClick"
    >
      <TableColumns />
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

    > .cell {
      white-space: nowrap;
    }
  }
}
</style>
