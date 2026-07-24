<script setup lang="ts">
import type { Component } from 'vue'
import { Check } from '@element-plus/icons-vue'

defineOptions({ name: 'MkDropdownItem', inheritAttrs: false })

withDefaults(
  defineProps<{
    /** 左侧 Element Plus 图标组件 */
    icon?: Component
    /** 是否属于可选中菜单；开启后始终预留右侧勾选位 */
    selectable?: boolean
    /** 当前项是否选中，仅在 selectable 为 true 时生效 */
    selected?: boolean
  }>(),
  {
    selectable: false,
    selected: false,
  },
)

defineSlots<{
  /** 菜单项内容 */
  default(): unknown
  /** 左侧自定义图标 */
  icon?(): unknown
}>()
</script>

<template>
  <el-dropdown-item
    class="mk-dropdown-item"
    :class="{ 'text-primary!': selectable && selected }"
    v-bind="$attrs"
  >
    <span v-if="icon || $slots.icon" class="flex shrink-0 items-center text-N600">
      <slot name="icon">
        <MkIcon v-if="icon" :icon="icon" />
      </slot>
    </span>
    <div class="flex-1 overflow-hidden">
      <slot />
    </div>
    <span v-if="selectable" class="flex size-4 shrink-0 items-center justify-center">
      <MkIcon v-if="selected" :icon="Check" />
    </span>
  </el-dropdown-item>
</template>
