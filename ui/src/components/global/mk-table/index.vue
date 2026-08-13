<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { TableInstance } from 'element-plus'

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
    data?: unknown[]
    maxTableHeight?: number
    paginationConfig?: PaginationConfig
    resizable?: boolean
    isSearching?: boolean
  }>(),
  {
    data: () => [],
    maxTableHeight: 250,
    resizable: false,
  },
)

const emit = defineEmits<{
  'current-change': [currentPage: number]
  'selection-change': [selection: unknown[]]
  'size-change': [pageSize: number]
  'update:paginationConfig': [paginationConfig: PaginationConfig]
}>()

const tableRef = ref<TableInstance>()

const paginationPageSizes = computed(() => props.paginationConfig?.pageSizes ?? DEFAULT_PAGE_SIZES)

/** 表格高度 */
const tableHeight = ref(window.innerHeight - props.maxTableHeight)
function updateTableHeight() {
  tableHeight.value = props.paginationConfig
    ? window.innerHeight - props.maxTableHeight
    : window.innerHeight - props.maxTableHeight + 50
}

/** 选择操作栏 */
const selectedRows = ref<unknown[]>([])
const isAllRowsSelected = computed(() => tableRef.value?.store.states.isAllSelected.value ?? false)
const isSelectionIndeterminate = computed(
  () => selectedRows.value.length > 0 && !isAllRowsSelected.value,
)

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

/**
 * 列宽拖拽
 * resizable 借用 Element Plus border 开启拖拽交互，并补充固定在列边界的 Hover 提示线。
 */
const tableRootRef = ref<HTMLElement>()
const resizeHoverStyle = ref<{ height: string; left: string; top: string }>()

function clearResizeHover() {
  resizeHoverStyle.value = undefined
}

function handleTableMouseMove(event: MouseEvent) {
  if (!props.resizable) {
    clearResizeHover()
    return
  }

  const resizeProxy = tableRootRef.value?.querySelector('.el-table__column-resize-proxy')

  if (resizeProxy instanceof HTMLElement && resizeProxy.style.display !== 'none') {
    clearResizeHover()
    return
  }

  const target = event.target instanceof Element ? event.target.closest('th.el-table__cell') : null

  if (document.body.style.cursor !== 'col-resize' || !(target instanceof HTMLElement)) {
    clearResizeHover()
    return
  }

  const rootRect = tableRootRef.value?.getBoundingClientRect()
  const targetRect = target.getBoundingClientRect()

  if (!rootRect) {
    return
  }

  resizeHoverStyle.value = {
    height: `${targetRect.height}px`,
    left: `${targetRect.right - rootRect.left}px`,
    top: `${targetRect.top - rootRect.top}px`,
  }
}

/** 分页 */
function handleCurrentPageChange(currentPage: number) {
  if (!props.paginationConfig) {
    return
  }

  emit('update:paginationConfig', {
    ...props.paginationConfig,
    currentPage,
  })
  emit('current-change', currentPage)
}

function handlePageSizeChange(pageSize: number) {
  if (!props.paginationConfig) {
    return
  }

  emit('update:paginationConfig', {
    ...props.paginationConfig,
    currentPage: 1,
    pageSize,
  })
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
  <MkEmpty
    v-if="props.paginationConfig ? !props.paginationConfig?.total : props.data.length === 0"
    :type="isSearching ? 'search' : ''"
    class="flex-1"
  />
  <div
    v-else
    ref="tableRootRef"
    class="mk-table relative w-full"
    @mouseleave="clearResizeHover"
    @mousemove="handleTableMouseMove"
  >
    <el-table
      ref="tableRef"
      :class="{ 'mk-table__resizable--borderless': props.resizable }"
      :data="props.data"
      :max-height="tableHeight"
      row-key="id"
      v-bind="$attrs"
      :border="props.resizable"
      @selection-change="handleSelectionChange"
    >
      <slot />
    </el-table>

    <div
      v-if="props.resizable && resizeHoverStyle"
      class="mk-table__resize-hover-indicator"
      :style="resizeHoverStyle"
    />

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

    <footer
      v-if="selectedRows.length > 0"
      class="fixed bottom-0 z-20 flex items-center border-t bg-white w-full -ml-6 px-6 py-4"
    >
      <div class="mr-4 flex items-center gap-3">
        <el-checkbox
          :indeterminate="isSelectionIndeterminate"
          :model-value="isAllRowsSelected"
          @change="handleToggleAllSelection"
        />
        <span>已选 {{ selectedRows.length }}/{{ props.data.length }}</span>
      </div>

      <slot name="footer-batch-actions" />
      <el-button text type="primary" class="shrink-0 ml-3!" @click="clearSelection">取消</el-button>
    </footer>
  </div>
</template>

<style scoped lang="scss">
:deep(.mk-table__resizable--borderless) {
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
}

.mk-table__resize-hover-indicator {
  background-color: color-mix(in srgb, var(--mk-primary) 20%, transparent);
  pointer-events: none;
  position: absolute;
  transform: translateX(-50%);
  width: 6px;
  z-index: 10;
}
</style>
