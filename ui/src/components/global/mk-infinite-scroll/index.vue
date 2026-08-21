<script setup lang="ts" generic="T">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { ResponsePage } from '@/api/admin/core/types'

defineOptions({ name: 'MkInfiniteScroll' })

interface InfiniteScrollPagination {
  currentPage: number
  pageSize: number
}

const dataList = defineModel<T[]>({ required: true })
const props = withDefaults(
  defineProps<{
    load: (pagination: InfiniteScrollPagination) => Promise<ResponsePage<T>>
    pageSize?: number
  }>(),
  {
    pageSize: 30,
  },
)

defineSlots<{
  default?: () => unknown
}>()

const triggerRef = ref<HTMLElement>()
const loading = ref(false)
// 是否到可见区域。
const isTriggerVisible = ref(false)

const pagination = ref({
  currentPage: 0,
  pageSize: props.pageSize,
  total: 0,
})
const finished = computed(
  () =>
    pagination.value.currentPage > 0 &&
    pagination.value.currentPage * pagination.value.pageSize >= pagination.value.total,
)
// 查询条件快速变化时可能并发 reset，只有最新版本的请求可以更新列表。
let requestVersion = 0
let infiniteScrollObserver: IntersectionObserver | undefined

function loadPage(currentPage: number) {
  const currentRequestVersion = ++requestVersion
  loading.value = true

  return props
    .load({ currentPage, pageSize: pagination.value.pageSize })
    .then((page) => {
      if (currentRequestVersion !== requestVersion) return

      // 第一页替换旧列表，滚动加载的后续页追加到现有列表。
      dataList.value = currentPage === 1 ? page.records : [...dataList.value, ...page.records]
      pagination.value = {
        currentPage: page.current,
        pageSize: page.size,
        total: page.total,
      }
    })
    .catch(() => {})
    .finally(() => {
      // 旧请求不能关闭新请求正在显示的 loading。
      if (currentRequestVersion === requestVersion) loading.value = false
    })
}

function tryLoadNextPage() {
  // 只有底部哨兵可见、当前无请求且仍有下一页时才继续加载。
  if (!isTriggerVisible.value || loading.value || finished.value) return
  return loadPage(pagination.value.currentPage + 1)
}

function reset() {
  // 搜索或筛选条件变化后清空旧数据，并从第一页重新查询。
  dataList.value = []
  pagination.value = {
    currentPage: 0,
    pageSize: props.pageSize,
    total: 0,
  }
  return loadPage(1)
}

onMounted(() => {
  infiniteScrollObserver = new IntersectionObserver(
    ([entry]) => {
      isTriggerVisible.value = entry?.isIntersecting ?? false
      tryLoadNextPage()
    },
    // 在哨兵到达可视区域前 200px 提前请求，减少滚动到底后的等待时间。
    { rootMargin: '0px 0px 200px' },
  )

  if (triggerRef.value) infiniteScrollObserver.observe(triggerRef.value)
  reset()
})

onBeforeUnmount(() => {
  infiniteScrollObserver?.disconnect()
})

defineExpose({ reset })
</script>

<template>
  <div v-loading="loading">
    <slot />
    <div ref="triggerRef" aria-live="polite" class="flex-center py-4 shrink-0 text-sm text-N600">
      <span v-if="loading">加载中...</span>
      <span v-else-if="finished">没有更多了</span>
    </div>
  </div>
</template>
