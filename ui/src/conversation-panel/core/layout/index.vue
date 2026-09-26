<template>
  <!-- 布局壳(纯展示):左/主/右三区 + 挤压/抽屉 + 遮罩。状态由外层传入,自身不含业务。 -->
  <div class="relative flex h-full overflow-hidden">
    <aside class="side-panel left shrink-0 overflow-hidden bg-N100" :class="[leftMode, { open: leftOpen }]" :style="{ '--side-w': leftWidth + 'px' }">
      <div class="side-panel__inner"><slot name="left" /></div>
    </aside>

    <div class="flex-column min-w-0 flex-1"><slot name="main" /></div>

    <aside
      v-if="hasRight"
      class="side-panel right shrink-0 overflow-hidden bg-N100"
      :class="[rightMode, { open: rightOpen }]"
      :style="{ '--side-w': rightWidth + 'px' }"
    >
      <div class="side-panel__inner"><slot name="right" /></div>
    </aside>

    <!-- 点击遮罩收起抽屉侧栏 -->
    <div v-if="showMask" class="absolute inset-0 z-30 bg-N900/40" @click="$emit('mask-click')" />
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'
import type { SidePanelMode } from './types'

const props = withDefaults(
  defineProps<{
    leftOpen: boolean
    rightOpen: boolean
    leftMode?: SidePanelMode
    rightMode?: SidePanelMode
    leftWidth?: number
    rightWidth?: number
  }>(),
  {
    leftMode: 'push',
    rightMode: 'push',
    leftWidth: 260,
    rightWidth: 320,
  },
)

defineEmits<{ 'mask-click': [] }>()

const slots = useSlots()
const hasRight = computed(() => !!slots.right)

const showMask = computed(() => (props.leftMode === 'drawer' && props.leftOpen) || (props.rightMode === 'drawer' && props.rightOpen))
</script>

<style scoped lang="scss">
.side-panel {
  /* 固定侧栏内容宽度，避免展开和收起时内容变形。 */
  &__inner {
    height: 100%;
    overflow-x: hidden;
    overflow-y: auto;
    width: var(--side-w);
  }

  /* 挤压侧栏参与布局，仅展开时显示分隔线。 */
  &.push {
    min-width: 0;
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    width: 0;

    &.open {
      width: var(--side-w);

      &.left {
        border-right: 1px solid var(--mk-N350);
      }

      &.right {
        border-left: 1px solid var(--mk-N350);
      }
    }
  }

  /* 抽屉侧栏覆盖主区，层级高于遮罩。 */
  &.drawer {
    bottom: 0;
    position: absolute;
    top: 0;
    transition:
      transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
      box-shadow 0.25s;
    width: var(--side-w);
    z-index: 40;

    &.left {
      border-right: 1px solid var(--mk-N350);
      left: 0;

      &:not(.open) {
        transform: translateX(-100%);
      }
    }

    &.open {
      box-shadow: var(--mk-box-shadow-lg);
      transform: translateX(0);
    }

    &.right {
      border-left: 1px solid var(--mk-N350);
      right: 0;

      &:not(.open) {
        transform: translateX(100%);
      }
    }
  }
}
</style>
