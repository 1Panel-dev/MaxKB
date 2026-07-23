<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'

defineOptions({ inheritAttrs: false })

withDefaults(
  defineProps<{
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
  /** 左侧图标；简单图标也可以直接使用 el-dropdown-item 的 icon 属性 */
  icon?(): unknown
  /** 无选中状态时的右侧内容，可放置图标、文字或自定义结构 */
  suffix?(): unknown
}>()
</script>

<template>
  <el-dropdown-item
    class="mk-dropdown-item"
    :class="{ 'text-primary!': selectable && selected }"
    v-bind="$attrs"
  >
    <span v-if="$slots.icon" class="flex shrink-0 items-center">
      <slot name="icon" />
    </span>
    <div class="min-w-0 flex-1 truncate">
      <slot />
    </div>
    <span v-if="selectable || $slots.suffix" class="flex shrink-0 items-center justify-center">
      <MkIcon v-if="selectable && selected" :icon="Check" />
      <slot v-else-if="!selectable" name="suffix" />
    </span>
  </el-dropdown-item>
</template>
