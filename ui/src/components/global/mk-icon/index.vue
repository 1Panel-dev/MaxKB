<script setup lang="ts">
import { computed, type Component } from 'vue'
import '@/assets/iconfont.js'

defineOptions({ name: 'MkIcon' })

/**
 * MkIcon 使用说明
 *
 * 组件已由 unplugin-vue-components 自动注册，Vue 模板中无需 import。
 *
 * 自定义 SVG Symbol：
 * <MkIcon name="icon_left_outlined" />
 * <MkIcon name="icon_start_outlined" :size="20" color="#3370ff" />
 *
 * Element Plus 图标（只需导入图标本身）：
 * import { Setting } from '@element-plus/icons-vue'
 * <MkIcon :icon="Setting" :size="20" />
 *
 * name 和 icon 二选一；size 默认 16，size、color 的行为与 el-icon 一致。
 */
const props = withDefaults(
  defineProps<{
    /** Element Plus 图标组件 */
    icon?: Component
    /** MaxKB SVG Symbol 名称，如 icon-left-outlined */
    name?: string
    /** 图标尺寸，默认 16px */
    size?: number | string
    color?: string
  }>(),
  {
    size: 16,
  },
)

const symbolHref = computed(() => `#${props.name}`)
</script>

<template>
  <el-icon class="mk-icon" :size="size" :color="color">
    <svg v-if="name" aria-hidden="true" focusable="false">
      <use :href="symbolHref" />
    </svg>
    <component :is="icon" v-else-if="icon" />
  </el-icon>
</template>
