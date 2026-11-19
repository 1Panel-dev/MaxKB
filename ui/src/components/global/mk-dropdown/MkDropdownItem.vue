<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'
import type { Component } from 'vue'

defineOptions({ name: 'MkDropdownItem', inheritAttrs: false })

withDefaults(
  defineProps<{
    /** 是否禁用菜单项 */
    disabled?: boolean
    /** 左侧 Element Plus 图标组件 */
    icon?: Component
    /** 是否属于可选中菜单；开启后始终预留右侧勾选位 */
    selectable?: boolean
    /** 当前项是否选中，仅在 selectable 为 true 时生效 */
    selected?: boolean
  }>(),
  { disabled: false, selectable: false, selected: false },
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
    class="mk-dropdown-item flex-align-center"
    :disabled="disabled"
    :class="{ 'text-primary!': selectable && selected }"
    v-bind="$attrs"
  >
    <span v-if="icon || $slots.icon" class="flex-align-center shrink-0" :class="disabled ? 'text-N400! [&_.el-icon]:text-N400!' : 'text-N600!'">
      <slot name="icon">
        <MkIcon v-if="icon" :icon="icon" />
      </slot>
    </span>
    <div class="flex-1 flex-align-center gap-2 overflow-hidden">
      <slot />
    </div>
    <span v-if="selectable" class="size-4 shrink-0">
      <MkIcon v-if="selected" :icon="Check" :class="{ 'text-N400!': disabled }" />
    </span>
  </el-dropdown-item>
</template>
