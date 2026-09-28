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
    leftWidth: 280,
    rightWidth: 420,
  },
)

defineEmits<{ 'mask-click': [] }>()

const slots = useSlots()
const hasRight = computed(() => !!slots.right)

const showMask = computed(() => (props.leftMode === 'drawer' && props.leftOpen) || (props.rightMode === 'drawer' && props.rightOpen))
</script>

<template>
  <!-- 布局壳(纯展示):左/主/右三区 + 挤压/抽屉 + 遮罩。状态由外层传入,自身不含业务。 -->
  <div class="relative flex h-full overflow-hidden">
    <aside
      class="mk-conversation-side-panel left shrink-0 overflow-hidden"
      :class="[leftMode, { open: leftOpen }]"
      :style="{ '--mk-chat-sidebar-width': leftWidth + 'px' }"
    >
      <div class="mk-conversation-side-panel__inner"><slot name="left" /></div>
    </aside>

    <slot name="main" />

    <aside
      v-if="hasRight"
      class="mk-conversation-side-panel right shrink-0 overflow-hidden"
      :class="[rightMode, { open: rightOpen }]"
      :style="{ '--mk-chat-right-width': rightWidth + 'px' }"
    >
      <div class="mk-conversation-side-panel__inner"><slot name="right" /></div>
    </aside>

    <!-- 点击遮罩收起抽屉侧栏 -->
    <div v-if="showMask" class="mk-conversation-mask" @click="$emit('mask-click')" />
  </div>
</template>
