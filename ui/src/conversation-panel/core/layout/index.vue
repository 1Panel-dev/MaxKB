<template>
  <!-- 布局壳(纯展示):左/主/右三区 + 挤压/抽屉 + 遮罩。状态由外层传入,自身不含业务。 -->
  <div class="conversation-layout">
    <aside
      class="side-panel left"
      :class="[leftMode, { open: leftOpen }]"
      :style="{ '--side-w': leftWidth + 'px' }"
    >
      <div class="side-panel__inner"><slot name="left" /></div>
    </aside>

    <div class="conv-main"><slot name="main" /></div>

    <aside
      v-if="hasRight"
      class="side-panel right"
      :class="[rightMode, { open: rightOpen }]"
      :style="{ '--side-w': rightWidth + 'px' }"
    >
      <div class="side-panel__inner"><slot name="right" /></div>
    </aside>

    <div v-if="showMask" class="conv-mask" @click="$emit('mask-click')" />
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

const showMask = computed(
  () =>
    (props.leftMode === 'drawer' && props.leftOpen) ||
    (props.rightMode === 'drawer' && props.rightOpen),
)
</script>

<style scoped lang="scss">
.conversation-layout {
  display: flex;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.conv-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.conv-mask {
  position: absolute;
  inset: 0;
  z-index: 30;
  background: rgba(0, 0, 0, 0.4);
}

/* ── 左右侧栏容器:挤压/抽屉,左右共用 ─────────────── */
.side-panel {
  flex-shrink: 0;
  box-sizing: border-box;
  background: var(--bg2, #fafafa);
  overflow: hidden;
}

/* 固定内容宽度,避免展开/收起动画期间内容被挤压变形 */
.side-panel__inner {
  width: var(--side-w);
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 挤压 push:参与 flex,宽度 0 ↔ width 动画。min-width:0 覆盖 flex 项默认 min-width:auto */
.side-panel.push {
  width: 0;
  min-width: 0;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.side-panel.push.open {
  width: var(--side-w);
}
.side-panel.left.push.open {
  border-right: 1px solid var(--bd, #dcdfe6);
}
.side-panel.right.push.open {
  border-left: 1px solid var(--bd, #dcdfe6);
}

/* 抽屉 drawer:绝对定位贴边,平移进出 */
.side-panel.drawer {
  position: absolute;
  top: 0;
  bottom: 0;
  width: var(--side-w);
  z-index: 40;
  transition:
    transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.25s;
}
.side-panel.left.drawer {
  left: 0;
  transform: translateX(-100%);
  border-right: 1px solid var(--bd, #dcdfe6);
}
.side-panel.right.drawer {
  right: 0;
  transform: translateX(100%);
  border-left: 1px solid var(--bd, #dcdfe6);
}
.side-panel.drawer.open {
  transform: translateX(0);
}
.side-panel.left.drawer.open {
  box-shadow: 4px 0 16px rgba(0, 0, 0, 0.2);
}
.side-panel.right.drawer.open {
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.2);
}
</style>
