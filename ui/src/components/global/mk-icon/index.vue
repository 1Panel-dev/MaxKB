<script setup lang="ts">
import { computed, type Component, useId } from 'vue'
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
 * name 和 icon 二选一；均未传入时显示 icon-404。
 * gradient 仅用于 SVG Symbol，启用后使用项目主题渐变填充。
 * size 默认 16，size、color 的行为与 el-icon 一致。
 */
const props = withDefaults(
  defineProps<{
    /** Element Plus 图标组件 */
    icon?: Component
    /** 是否使用项目主题渐变填充 SVG Symbol */
    gradient?: boolean
    /** MaxKB SVG Symbol 名称，如 icon-left-outlined */
    name?: string
    /** 图标尺寸，默认 16px */
    size?: number | string
    color?: string
  }>(),
  { size: 16 },
)

const gradientId = useId()
const iconName = computed(() => props.name || (!props.icon ? 'icon-404' : undefined))
const symbolFill = computed(() => (props.gradient ? `url(#${gradientId})` : undefined))
const symbolHref = computed(() => `#${iconName.value}`)
</script>

<template>
  <el-icon class="mk-icon shrink-0" :size="size" :color="color">
    <svg v-if="iconName" aria-hidden="true" focusable="false" :fill="symbolFill">
      <defs v-if="gradient">
        <linearGradient :id="gradientId" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="var(--mk-primary)" />
          <stop offset="100%" stop-color="var(--mk-primary-gradient-end)" />
        </linearGradient>
      </defs>
      <use :href="symbolHref" />
    </svg>
    <component :is="icon" v-else-if="icon" />
  </el-icon>
</template>
