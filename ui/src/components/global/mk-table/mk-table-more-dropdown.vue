<script setup lang="ts">
import { computed, useSlots } from 'vue'
import { hasRenderableSlotContent } from '@/utils/vnode'

defineOptions({ name: 'MkTableMoreDropdown', inheritAttrs: false })

defineProps<{ menuClass?: string }>()

defineSlots<{
  /** 表格 More 菜单项，仅使用 MkDropdownItem */
  default(): unknown
}>()

const slots = useSlots()
const hasDropdownItems = computed(() => hasRenderableSlotContent(slots.default?.()))
</script>

<template>
  <MkDropdown v-if="hasDropdownItems" trigger="click" placement="bottom-end" v-bind="$attrs">
    <el-button type="primary" text @click.stop>
      <MkIcon name="icon_more_outlined" />
    </el-button>

    <template #dropdown>
      <MkDropdownMenu :class="menuClass">
        <slot />
      </MkDropdownMenu>
    </template>
  </MkDropdown>
</template>
