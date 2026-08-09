<script setup lang="ts" generic="T extends Record<string, unknown>">
import type { ScrollbarDirection, ScrollbarInstance } from 'element-plus'
import { computed, nextTick, ref, watch } from 'vue'

defineOptions({ name: 'MkSearchList' })

/**
 * 带搜索、选中态和悬浮操作区的通用列表。
 * 默认使用 name 作为展示和搜索字段、id 作为唯一值；数据结构不同时通过 props 映射。
 *
 * @example
 * <!-- data 示例为 [{ id: '1', name: '管理员' }]，使用 name/id 时可省略 props -->
 * <MkSearchList
 *   v-model="searchKeyword"
 *   :data="data"
 *   default-active="1"
 *   :props="{ label: 'name', value: 'id' }"
 *   @click="selectRow"
 * />

 */
const componentProps = withDefaults(
  defineProps<{
    /** 列表全量数据，搜索在前端完成 */
    data?: T[]
    /** 初始选中项的唯一值 */
    defaultActive?: string | number
    /** 列表为空或无搜索结果时的提示 */
    emptyText?: string
    /** 将业务数据的字段名映射为组件的展示字段和唯一值字段 */
    props?: {
      label?: keyof T & string
      value?: keyof T & string
    }
  }>(),
  {
    defaultActive: '',
    emptyText: '暂无数据',
    props: () => ({}),
  },
)

const emit = defineEmits<{
  click: [row: T, index: number]
}>()

defineSlots<{
  action(props: { row: T; index: number }): unknown
  'action-dropdown'(props: { row: T; index: number }): unknown
  empty(): unknown
  row(props: { row: T; index: number; active: boolean }): unknown
}>()

const currentValue = ref<unknown>(componentProps.defaultActive)

const labelField = computed(() => componentProps.props.label ?? ('name' as keyof T & string))
const valueField = computed(() => componentProps.props.value ?? ('id' as keyof T & string))

// 搜索仅匹配映射后的 label 字段，并忽略大小写和关键词首尾空格。
const searchKeyword = defineModel<string>({ default: '' })
const filteredData = computed(() => {
  if (!componentProps.data) return []

  const normalizedKeyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!normalizedKeyword) return componentProps.data

  return componentProps.data.filter((row) => {
    return String(row[labelField.value] ?? '')
      .toLocaleLowerCase()
      .includes(normalizedKeyword)
  })
})

// 全量数据先过滤，再每次渲染 50 条，滚动到底部时继续追加。
const pageSize = 50
const currentPage = ref(1)
const renderData = computed(() => filteredData.value.slice(0, currentPage.value * pageSize))
const hasMore = computed(() => renderData.value.length < filteredData.value.length)

function loadMore(direction: ScrollbarDirection) {
  if (direction === 'bottom' && hasMore.value) currentPage.value += 1
}

// 数据源或搜索词变化时回到第一批，避免保留上一次的渲染页数和滚动位置。
const scrollbarRef = ref<ScrollbarInstance>()
watch([() => componentProps.data, () => componentProps.data?.length, searchKeyword], () => {
  currentPage.value = 1
  nextTick(() => scrollbarRef.value?.setScrollTop(0))
})

watch(
  () => componentProps.defaultActive,
  (value) => {
    currentValue.value = value
  },
)

function selectRow(row: T, index: number) {
  currentValue.value = row[valueField.value]
  emit('click', row, index)
}

// 点击型 Dropdown 由列表内部持有，移出当前行及其菜单后统一关闭。
const actionDropdownInstances = new Map<unknown, { handleClose: () => void }>()
const hoveredActionValue = ref<unknown>()
const focusedActionValue = ref<unknown>()

function setActionDropdownRef(row: T, instance: unknown) {
  const actionKey = row[valueField.value]
  const dropdownInstance = instance as { handleClose?: () => void } | null

  if (typeof dropdownInstance?.handleClose === 'function') {
    actionDropdownInstances.set(actionKey, dropdownInstance as { handleClose: () => void })
  } else {
    actionDropdownInstances.delete(actionKey)
  }
}

function isActionVisible(row: T) {
  const actionValue = row[valueField.value]
  return hoveredActionValue.value === actionValue || focusedActionValue.value === actionValue
}

function showAction(row: T) {
  hoveredActionValue.value = row[valueField.value]
}

function focusAction(row: T) {
  focusedActionValue.value = row[valueField.value]
}

function blurAction(event: FocusEvent) {
  const actionElement = event.currentTarget as HTMLElement
  if (!event.relatedTarget || !actionElement.contains(event.relatedTarget as Node)) {
    focusedActionValue.value = undefined
  }
}

function closeActionDropdown(row: T, event: MouseEvent) {
  const actionValue = row[valueField.value]
  hoveredActionValue.value = undefined
  if (focusedActionValue.value === actionValue) focusedActionValue.value = undefined
  actionDropdownInstances.get(actionValue)?.handleClose()

  const rowElement = event.currentTarget as HTMLElement
  nextTick(() => {
    requestAnimationFrame(() => {
      if (
        document.activeElement instanceof HTMLElement &&
        rowElement.contains(document.activeElement)
      ) {
        document.activeElement.blur()
      }
    })
  })
}
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <MkSearchInput v-model="searchKeyword" class="shrink-0 px-4" />

    <el-scrollbar ref="scrollbarRef" class="min-h-0 flex-1 px-4 py-2" @end-reached="loadMore">
      <div v-if="filteredData.length" class="flex flex-col gap-1">
        <template v-for="(row, index) in renderData" :key="String(row[valueField] ?? index)">
          <div
            class="flex p-2 cursor-pointer items-center rounded-md hover:bg-N900/10"
            :class="{
              'bg-primary/10 hover:bg-primary/10 font-medium text-primary':
                currentValue === row[valueField],
            }"
            @click="selectRow(row, index)"
            @mouseenter="showAction(row)"
            @mouseleave="closeActionDropdown(row, $event)"
          >
            <slot name="row" :row="row" :index="index" :active="currentValue === row[valueField]">
              <span class="min-w-0 flex-1 truncate">{{ row[labelField] }}</span>
            </slot>
            <!-- 操作区保留布局宽度，hover/focus 时显示，并阻止触发行点击。 -->
            <div
              v-if="$slots.action || $slots['action-dropdown']"
              class="ml-auto flex shrink-0 items-center transition-opacity"
              :class="
                isActionVisible(row)
                  ? 'pointer-events-auto opacity-100'
                  : 'pointer-events-none opacity-0'
              "
              @click.stop
              @focusin="focusAction(row)"
              @focusout="blurAction"
              @keydown.stop
            >
              <MkDropdown
                v-if="$slots['action-dropdown']"
                :ref="(instance) => setActionDropdownRef(row, instance)"
                trigger="click"
                :teleported="false"
              >
                <el-button class="-mr-1" text>
                  <MkIcon name="icon_more_outlined" />
                </el-button>
                <template #dropdown>
                  <slot name="action-dropdown" :row="row" :index="index" />
                </template>
              </MkDropdown>
              <slot v-else name="action" :row="row" :index="index" />
            </div>
          </div>
        </template>
      </div>
      <slot v-else name="empty">
        <el-empty :description="emptyText" :image-size="80" />
      </slot>
    </el-scrollbar>
  </div>
</template>
