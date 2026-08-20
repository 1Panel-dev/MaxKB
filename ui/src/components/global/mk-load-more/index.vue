<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

defineOptions({ name: 'MkLoadMore' })

interface LoadMorePaginationConfig {
  currentPage: number
  pageSize: number
  total: number
}

const props = withDefaults(
  defineProps<{
    disabled?: boolean
    distance?: number
    loading?: boolean
    paginationConfig: LoadMorePaginationConfig
  }>(),
  {
    disabled: false,
    distance: 200,
    loading: false,
  },
)

const emit = defineEmits<{
  load: [page: number]
}>()

defineSlots<{
  finished?: () => unknown
  loading?: () => unknown
}>()

const triggerRef = ref<HTMLElement>()
const isIntersecting = ref(false)
const pendingPage = ref<number>()
const finished = computed(
  () =>
    props.paginationConfig.currentPage * props.paginationConfig.pageSize >=
    props.paginationConfig.total,
)
let loadMoreObserver: IntersectionObserver | undefined

function tryLoadNextPage() {
  if (
    !isIntersecting.value ||
    props.disabled ||
    props.loading ||
    finished.value ||
    pendingPage.value !== undefined
  ) {
    return
  }

  const nextPage = props.paginationConfig.currentPage + 1
  pendingPage.value = nextPage
  emit('load', nextPage)
}

watch(
  () => props.loading,
  (loading, previousLoading) => {
    if (loading || !previousLoading || pendingPage.value === undefined) return

    const loaded = props.paginationConfig.currentPage >= pendingPage.value
    pendingPage.value = undefined

    // 当前数据不足以撑满滚动区域时，成功后继续补齐下一页。
    if (loaded) nextTick(tryLoadNextPage)
  },
)

onMounted(() => {
  loadMoreObserver = new IntersectionObserver(
    ([entry]) => {
      isIntersecting.value = entry?.isIntersecting ?? false
      tryLoadNextPage()
    },
    { rootMargin: `0px 0px ${props.distance}px` },
  )

  if (triggerRef.value) loadMoreObserver.observe(triggerRef.value)
})

onBeforeUnmount(() => {
  loadMoreObserver?.disconnect()
})
</script>

<template>
  <div
    ref="triggerRef"
    aria-live="polite"
    class="flex h-12 shrink-0 items-center justify-center text-sm text-N600"
  >
    <slot v-if="loading" name="loading">加载中...</slot>
    <slot v-else-if="finished" name="finished">没有更多了</slot>
  </div>
</template>
