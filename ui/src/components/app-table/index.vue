<template>
  <div class="app-table" :class="quickCreate ? 'table-quick-append' : ''">
    <el-table
      :max-height="tableHeight"
      v-bind="$attrs"
      ref="appTableRef"
      @header-dragend="handleHeaderDragend"
      :tooltip-options="{
        popperClass: 'max-w-350',
      }"
    >
      <template #append v-if="quickCreate">
        <div v-if="showInput">
          <el-input
            ref="quickInputRef"
            v-model="inputValue"
            :placeholder="`${$t('common.inputPlaceholder')} ${quickCreateName}`"
            class="w-500 mr-12"
            autofocus
            :maxlength="quickCreateMaxlength || '-'"
            :show-word-limit="quickCreateMaxlength ? true : false"
            @keydown.enter="submitHandle"
            clearable
          />

          <el-button type="primary" @click="submitHandle" :disabled="loading"
            >{{ $t('common.create') }}
          </el-button>
          <el-button @click="showInput = false" :disabled="loading"
            >{{ $t('common.cancel') }}
          </el-button>
        </div>
        <div v-else @click="quickCreateHandle" class="w-full">
          <el-button type="primary" link class="quich-button">
            <AppIcon iconName="app-add-outlined"></AppIcon>
            <span class="ml-4">{{ quickCreatePlaceholder }}</span>
          </el-button>
        </div>
      </template>
      <slot></slot>
    </el-table>
    <div class="app-table__pagination mt-16" v-if="$slots.pagination || paginationConfig">
      <slot name="pagination">
        <el-pagination
          v-model:current-page="paginationConfig.current_page"
          v-model:page-size="paginationConfig.page_size"
          :page-sizes="paginationConfig.page_sizes || pageSizes"
          :total="paginationConfig.total"
          layout="total, prev, pager, next, sizes"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </slot>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, watch, computed, onMounted, useAttrs } from 'vue'
import { MsgError } from '@/utils/message'
import { t } from '@/locales'

defineOptions({ name: 'AppTable' })

import useStore from '@/stores'

const { common } = useStore()

const attrs = useAttrs()

const props = defineProps({
  paginationConfig: {
    type: Object,
    default: () => {},
  },
  quickCreate: {
    type: Boolean,
    default: false,
  },
  quickCreateName: {
    type: String,
    default: () => t('components.quickCreateName'),
  },
  quickCreatePlaceholder: {
    type: String,
    default: () => t('components.quickCreatePlaceholder'),
  },
  quickCreateMaxlength: {
    type: Number,
    default: () => 0,
  },
  storeKey: String,
  maxTableHeight: {
    type: Number,
    default: 300,
  },
})
const emit = defineEmits(['changePage', 'sizeChange', 'creatQuick'])

const paginationConfig = computed(() => props.paginationConfig)

const pageSizes = [10, 20, 50, 100]

const quickInputRef = ref()
const appTableRef = ref()

const loading = ref(false)
const showInput = ref(false)
const inputValue = ref('')
const tableHeight = ref<number | string>('')
watch(showInput, (bool: boolean) => {
  if (!bool) {
    inputValue.value = ''
  }
})

function submitHandle() {
  if (inputValue.value) {
    loading.value = true
    emit('creatQuick', inputValue.value)
    setTimeout(() => {
      showInput.value = false
      loading.value = false
    }, 200)
  } else {
    MsgError(`${props.quickCreateName} ${t('dynamicsForm.tip.requiredMessage')}`)
  }
}

function quickCreateHandle() {
  showInput.value = true
  nextTick(() => {
    quickInputRef.value?.focus()
  })
}

function handleSizeChange() {
  emit('sizeChange')
  if (props.storeKey) {
    common.savePage(props.storeKey, props.paginationConfig)
  }
}

function handleCurrentChange() {
  emit('changePage')
  if (props.storeKey) {
    common.savePage(props.storeKey, props.paginationConfig)
  }
}

function clearSelection() {
  appTableRef.value?.clearSelection()
}

/* ----------------- 列宽拖拽持久化 ----------------- */
const COLUMN_WIDTH_PREFIX = 'app-table-column-width:'

function widthStorageKey() {
  return `${COLUMN_WIDTH_PREFIX}${props.storeKey}`
}

function loadWidthMap(): Record<string, number> {
  try {
    return JSON.parse(localStorage.getItem(widthStorageKey()) || '{}')
  } catch {
    return {}
  }
}

function saveWidthMap(map: Record<string, number>) {
  try {
    localStorage.setItem(widthStorageKey(), JSON.stringify(map))
  } catch {
    /* ignore quota / serialization errors */
  }
}

/**
 * 列的稳定标识：优先用 prop / column-key，其次回退到渲染顺序下标。
 */
function getColumnKey(column: any, index: number) {
  return column?.property || column?.columnKey || `__col_${index}__`
}

/**
 * 拖拽结束后，记录该列的最新宽度
 */
function handleHeaderDragend(newWidth: number, _oldWidth: number, column: any) {
  if (!props.storeKey || !column || !newWidth) {
    return
  }
  const cols = appTableRef.value?.columns || []
  const index = cols.findIndex((c: any) => c.id === column.id)
  const key = getColumnKey(column, index)
  const map = loadWidthMap()
  map[key] = Math.round(newWidth)
  saveWidthMap(map)
}

/**
 * 表格渲染后，把缓存的列宽应用回去
 */
function restoreColumnWidths() {
  if (!props.storeKey) {
    return
  }
  const map = loadWidthMap()
  if (!map || !Object.keys(map).length) {
    return
  }
  const table = appTableRef.value
  const cols = table?.columns || []
  let changed = false
  cols.forEach((column: any, index: number) => {
    const w = map[getColumnKey(column, index)]
    if (typeof w === 'number' && w > 0 && column.realWidth !== w) {
      column.width = w
      column.realWidth = w
      changed = true
    }
  })
  if (changed) {
    table?.doLayout?.()
  }
}

function toggleRowSelection(row: any, selected?: boolean, ignoreSelectable = true) {
  appTableRef.value?.toggleRowSelection(row, selected, ignoreSelectable)
}

function getSelectionRows() {
  return appTableRef.value?.getSelectionRows()
}

defineExpose({
  clearSelection,
  toggleRowSelection,
  getSelectionRows,
})

onMounted(() => {
  tableHeight.value = window.innerHeight - props.maxTableHeight
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - props.maxTableHeight
    })()
  }

  // 首次渲染后恢复缓存的列宽
  nextTick(restoreColumnWidths)
})

// 数据变化（翻页 / 筛选 / 轮询刷新）会重建列，重新应用缓存列宽
watch(
  () => attrs.data,
  () => {
    nextTick(restoreColumnWidths)
  },
)

</script>

<style lang="scss" scoped>
.app-table {
  &__pagination {
    display: flex;
    justify-content: flex-end;
  }

  .quich-button {
    &:hover {
      color: var(--el-button-text-color);
    }
  }
}
</style>
