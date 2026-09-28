<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, useTemplateRef } from 'vue'
import type { ScrollbarInstance } from 'element-plus'

defineOptions({ name: 'MkHorizontalScroll' })
defineSlots<{ default(): unknown }>()

const contentRef = useTemplateRef<HTMLDivElement>('contentRef')
const scrollbarRef = useTemplateRef<ScrollbarInstance>('scrollbarRef')
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
let resizeObserver: ResizeObserver | undefined

// 根据当前滚动位置分别控制左右箭头，边界保留 1px 容差。
function updateScrollState() {
  const viewport = scrollbarRef.value?.wrapRef
  if (!viewport) return
  canScrollLeft.value = viewport.scrollLeft > 1
  canScrollRight.value = viewport.scrollWidth - viewport.clientWidth - viewport.scrollLeft > 1
}

function scrollContent(direction: -1 | 1) {
  const viewport = scrollbarRef.value?.wrapRef
  if (!viewport) return
  viewport.scrollBy({ left: direction * viewport.clientWidth * 0.8, behavior: 'smooth' })
}

// 内容增删、图片加载和容器缩放都会触发尺寸更新。
onMounted(() => {
  resizeObserver = new ResizeObserver(updateScrollState)
  for (const element of [contentRef.value, scrollbarRef.value?.wrapRef]) {
    if (element) resizeObserver.observe(element)
  }
  updateScrollState()
})
onBeforeUnmount(() => resizeObserver?.disconnect())
</script>

<template>
  <div class="mk-horizontal-scroll relative flex-align-center min-w-0">
    <!-- 向左滚动内容 -->
    <div v-if="canScrollLeft" class="mk-horizontal-scroll-prev absolute inset-y-0 left-0 z-2 flex-center w-13">
      <el-button text @click="scrollContent(-1)" class="-ml-7">
        <MkIcon name="icon_left_outlined" :size="18" />
      </el-button>
    </div>

    <el-scrollbar ref="scrollbarRef" class="min-w-0 flex-1 h-auto!" @scroll="updateScrollState">
      <div ref="contentRef" class="flex-align-center w-max gap-2">
        <slot />
      </div>
    </el-scrollbar>
    <!-- 向右滚动内容 -->
    <div v-if="canScrollRight" class="mk-horizontal-scroll-next absolute inset-y-0 right-0 z-2 flex-center w-13">
      <el-button text @click="scrollContent(1)" class="-mr-7">
        <MkIcon name="icon_right_outlined" :size="18" />
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.mk-horizontal-scroll {
  &-prev {
    background: linear-gradient(90deg, #ffffff 45.45%, rgba(255, 255, 255, 0) 98.96%);
  }
  &-next {
    background: linear-gradient(270deg, #ffffff 45.45%, rgba(255, 255, 255, 0) 98.96%);
  }

  :deep(.el-scrollbar__bar.is-horizontal) {
    display: none;
  }
}
</style>
