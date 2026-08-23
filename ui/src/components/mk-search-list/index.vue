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
  default(props: { row: T; index: number; active: boolean }): unknown
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
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <MkSearchInput v-model="searchKeyword" class="shrink-0 px-4" />

    <el-scrollbar ref="scrollbarRef" class="min-h-0 flex-1 px-4 py-2" @end-reached="loadMore">
      <div v-if="filteredData.length" class="flex flex-col gap-1">
        <template v-for="(row, index) in renderData" :key="String(row[valueField] ?? index)">
          <MkListItem
            :active="currentValue === row[valueField]"
            :index="index"
            :label-field="labelField"
            :row="row"
            @click="selectRow(row, index)"
          >
            <template v-if="$slots.default" #default="slotProps">
              <slot v-bind="slotProps" />
            </template>
            <template v-if="$slots.action" #action="slotProps">
              <slot name="action" v-bind="slotProps" />
            </template>
            <template v-if="$slots['action-dropdown']" #action-dropdown="slotProps">
              <slot name="action-dropdown" v-bind="slotProps" />
            </template>
          </MkListItem>
        </template>
      </div>
      <slot v-else name="empty">
        <p class="text-center mt-20 text-N600">
          {{ searchKeyword ? '没有找到相关内容' : emptyText }}
        </p>
      </slot>
    </el-scrollbar>
  </div>
</template>
