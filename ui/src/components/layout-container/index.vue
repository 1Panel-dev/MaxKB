<template>
  <div class="layout-container flex h-full">
    <div
      :class="`layout-container__left border-r ${isCollapse ? 'hidden' : ''}`"
      :style="{ width: isCollapse ? 0 : `${leftWidth}px` }"
    >
      <div class="layout-container__left_content">
        <slot name="left"></slot>
      </div>
      <el-tooltip
        :content="isCollapse ? $t('common.expand') : $t('common.collapse')"
        placement="right"
      >
        <el-button
          v-if="props.showCollapse"
          class="collapse"
          size="small"
          circle
          @click="isCollapse = !isCollapse"
          :icon="isCollapse ? 'ArrowRightBold' : 'ArrowLeftBold'"
        />
      </el-tooltip>
      <div
        v-if="props.resizable"
        class="splitter-bar-line"
        :class="isResizing ? 'hover' : ''"
        @mousedown="onSplitterMouseDown"
      ></div>
    </div>
    <div class="layout-container__right">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from 'vue'
defineOptions({ name: 'LayoutContainer' })

const props = defineProps({
  showCollapse: Boolean,
  resizable: Boolean,
  minLeftWidth: {
    type: Number,
    default: 240,
  },
  maxLeftWidth: {
    type: Number,
    default: 400,
  },
})

const isCollapse = ref(false)
const leftWidth = ref(props.minLeftWidth)
const isResizing = ref(false)

const onSplitterMouseDown = (e: MouseEvent) => {
  if (!props.resizable) return
  e.preventDefault()
  isResizing.value = true
  document.body.style.userSelect = 'none'
  const startX = e.clientX
  const startWidth = leftWidth.value
  const onMouseMove = (moveEvent: MouseEvent) => {
    if (!isResizing.value) return
    const deltaX = moveEvent.clientX - startX
    let newWidth = startWidth + deltaX

    // 限制宽度在最小和最大值之间
    newWidth = Math.max(props.minLeftWidth, Math.min(props.maxLeftWidth, newWidth))
    leftWidth.value = newWidth
  }

  const onMouseUp = () => {
    isResizing.value = false
    document.body.style.userSelect = ''
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', () => {})
  document.removeEventListener('mouseup', () => {})
})
</script>

<style lang="scss" scoped>
.layout-container {
  &__left {
    position: relative;
    box-sizing: border-box;
    // transition: width 0.28s;
    width: var(--sidebar-width);
    .splitter-bar-line {
      z-index: 1;
      position: absolute;
      top: 0;
      right: 0;
      cursor: col-resize;
      width: 4px;
      height: 100%;
      &.hover:after {
        width: 1px;
        height: 100%;
        content: '';
        z-index: 2;
        position: absolute;
        right: -1px;
        top: 0;
        background: var(--el-color-primary);
      }
    }

    .collapse {
      position: absolute;
      top: 36px;
      right: -12px;
      box-shadow: 0px 5px 10px 0px var(--app-text-color-light-1);
      z-index: 2;
    }

    .layout-container__left_content {
      width: 100%;
      // height: 100%;
    }

    &.hidden {
      width: 0;
      min-width: 0;

      .layout-container__left_content {
        visibility: hidden;
      }

      .collapse {
        right: -18px;
      }
    }
  }

  &__right {
    flex: 1;
    overflow: hidden;
  }
}
</style>
