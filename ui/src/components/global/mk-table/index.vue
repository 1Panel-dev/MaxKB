<script setup lang="ts">
import { computed, ref } from 'vue'
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
    paginationConfig?: PaginationConfig
    resizable?: boolean
  }>(),
  {
    data: () => [],
    paginationConfig: () => ({
      currentPage: 1,
      pageSize: 20,
      pageSizes: [10, 20, 50, 100],
      total: 0,
    }),
    resizable: false,
  },
)

const emit = defineEmits<{
  'current-change': [currentPage: number]
  'size-change': [pageSize: number]
  'update:paginationConfig': [paginationConfig: PaginationConfig]
}>()

const tableRef = ref<TableInstance>()
const paginationPageSizes = computed(() => props.paginationConfig.pageSizes ?? DEFAULT_PAGE_SIZES)

/**
 * 列宽拖拽
 * resizable 开启 Element Plus border 和拖拽交互，并补充固定在列边界的 Hover 提示线。
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
  emit('update:paginationConfig', {
    ...props.paginationConfig,
    currentPage,
  })
  emit('current-change', currentPage)
}

function handlePageSizeChange(pageSize: number) {
  emit('update:paginationConfig', {
    ...props.paginationConfig,
    pageSize,
  })
  emit('size-change', pageSize)
}

defineExpose({ tableRef })
</script>

<template>
  <div
    ref="tableRootRef"
    class="mk-table relative w-full"
    @mouseleave="clearResizeHover"
    @mousemove="handleTableMouseMove"
  >
    <el-table ref="tableRef" :data="props.data" v-bind="$attrs" :border="props.resizable">
      <slot />
    </el-table>
    <div
      v-if="props.resizable && resizeHoverStyle"
      class="mk-table__resize-hover-indicator"
      :style="resizeHoverStyle"
    />

    <div class="mt-4 flex justify-end">
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
  </div>
</template>

<style scoped lang="scss">
// :deep(.el-table__column-resize-proxy) {
//   background-color: var(--mk-primary);
//   border-left: 0;
//   transform: translateX(-1px);
//   width: 2px;
// }

.mk-table__resize-hover-indicator {
  background-color: color-mix(in srgb, var(--mk-primary) 20%, transparent);
  pointer-events: none;
  position: absolute;
  transform: translateX(-50%);
  width: 6px;
  z-index: 10;
}
</style>
