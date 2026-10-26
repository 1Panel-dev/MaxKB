<script setup lang="ts">
import { useReverseInfiniteScroll, type ReverseInfiniteScrollProps } from './index'

defineOptions({ name: 'ReverseInfiniteScroll' })
const props = defineProps<ReverseInfiniteScrollProps>()
defineSlots<{
  default?: () => unknown
  empty?: () => unknown
}>()

const { scrollbarRef, initialLoading, loadingMore, onScroll, scrollToBottom, followBottom } = useReverseInfiniteScroll(props)

defineExpose({ scrollToBottom, followBottom })
</script>

<template>
  <div v-loading="initialLoading" class="min-h-0 flex-1 overflow-hidden">
    <el-scrollbar ref="scrollbarRef" wrap-class="[overflow-anchor:none]" view-class="min-h-full flex-column" @scroll="onScroll">
      <div class="min-h-full flex-1 flex-column">
        <template v-if="count > 0">
          <!-- 固定预留状态行，加载提示切换时不改变消息位置。 -->
          <div v-if="loadingMore" class="flex-center py-4 shrink-0">
            <span class="mk-conversation-loading" />
          </div>
          <slot />
        </template>
        <slot v-else-if="!loading" name="empty" />
      </div>
    </el-scrollbar>
  </div>
</template>
