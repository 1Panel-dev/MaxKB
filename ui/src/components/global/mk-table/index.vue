<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { TableInstance } from 'element-plus'
import LayoutBatchFooter from '../mk-view-layout/layout-batch-footer.vue'

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
    resizable?: boolean // 非指定表格禁止开启
    size?: 'small'
  }>(),
  { data: () => [], maxTableHeight: 250, resizable: false },
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
  <div class="mk-table relative flex w-full min-h-0 flex-1 flex-col">
    <el-table
      ref="tableRef"
      :class="{ 'mk-table__resizable--borderless': props.resizable, small: props.size === 'small' }"
      :data="props.data"
      :max-height="tableHeight"
      row-key="id"
      v-bind="$attrs"
      :border="props.resizable"
      @selection-change="handleSelectionChange"
    >
      <slot />
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
}
</style>
