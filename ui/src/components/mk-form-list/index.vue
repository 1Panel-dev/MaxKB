<script setup lang="ts" generic="T">
import { cloneDeep } from 'lodash'
import { computed, useTemplateRef } from 'vue'
import { useSortable, type SortableChange } from '@/utils/use-sortable'

defineOptions({ name: 'MkFormList' })

const props = withDefaults(
  defineProps<{
    addText?: string
    defaultItem: T | (() => T)
    firstRowHasLabel?: boolean
    showAddButton?: boolean
    sortable?: boolean
    itemKey?: keyof T | ((item: T) => string | number)
  }>(),
  {
    addText: '添加',
    firstRowHasLabel: true,
    showAddButton: true,
    sortable: false,
  },
)
const formRows = defineModel<T[]>({ required: true })

const emit = defineEmits<{ remove: [item: T, index: number]; 'sort-change': [change: SortableChange<T>] }>()

defineSlots<{ default(props: { index: number; item: T }): unknown }>()

// 只绑定表单行容器，添加按钮不参与排序。
const rowsRef = useTemplateRef<HTMLElement>('rowsRef')
function resolveRowKey(item: T) {
  return typeof props.itemKey === 'function' ? props.itemKey(item) : props.itemKey === undefined ? undefined : item[props.itemKey]
}
function getRowKey(item: T, index: number): string | number {
  const key = resolveRowKey(item)
  return typeof key === 'string' || typeof key === 'number' ? key : index
}
const sortDisabled = computed(() => {
  if (props.itemKey === undefined || formRows.value.length < 2) return true
  const keys = formRows.value.map(resolveRowKey)
  return keys.some((key) => typeof key !== 'string' && typeof key !== 'number') || new Set(keys).size !== keys.length
})
useSortable(
  () => (props.sortable ? rowsRef.value : null),
  formRows,
  () => ({
    disabled: sortDisabled.value,
    handle: '.mk-form-list__handle',
    draggable: '> .mk-form-list__row',
    cloneOnUpdate: true,
    onReorder: (change) => emit('sort-change', change),
  }),
)

function addRow() {
  // 回写独立数据，避免 LogicFlow 历史记录重复观察同一个对象。
  const newRow = typeof props.defaultItem === 'function' ? (props.defaultItem as () => T)() : props.defaultItem
  formRows.value = [...cloneDeep(formRows.value), cloneDeep(newRow)]
}

function removeRow(index: number) {
  if (formRows.value.length === 1) return
  const removedItem = formRows.value[index] as T
  formRows.value = cloneDeep(formRows.value.filter((_, rowIndex) => rowIndex !== index))
  emit('remove', removedItem, index)
}
</script>

<template>
  <div ref="rowsRef" class="w-full">
    <div v-for="(item, index) in formRows" :key="getRowKey(item, index)" class="mk-form-list__row flex w-full gap-2">
      <el-button
        v-if="sortable"
        link
        class="mk-form-list__handle shrink-0 text-N600 -mr-2 h-8!"
        :class="{ 'mt-8': firstRowHasLabel && index === 0 }"
        :disabled="sortDisabled"
        aria-label="拖拽排序"
      >
        <MkIcon name="icon_drag_outlined" />
      </el-button>
      <slot :index="index" :item="item" />
      <el-form-item class="shrink-0" :class="firstRowHasLabel ? (index === 0 ? 'mt-8' : 'mt-0.5') : 'mt-1'">
        <el-button :disabled="formRows.length === 1" text @click="removeRow(index)">
          <MkIcon name="icon_delete-trash_outlined" class="text-N600" />
        </el-button>
      </el-form-item>
    </div>
  </div>

  <el-button v-if="showAddButton" class="-mt-1" link type="primary" @click="addRow">
    <MkIcon name="icon_add_outlined" />
    <span>{{ addText }}</span>
  </el-button>
</template>
