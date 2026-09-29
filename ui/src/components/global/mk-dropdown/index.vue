<script setup lang="ts">
import { Fragment, isVNode, ref } from 'vue'
import type { DropdownInstance } from 'element-plus'
import type { Options } from '@popperjs/core'
import { hasRenderableSlotContent } from '@/utils/vnode'
import MkDropdownMenu from './MkDropdownMenu.vue'

defineOptions({ name: 'MkDropdown', inheritAttrs: false })

withDefaults(defineProps<{ popperOptions?: Partial<Options>; persistent?: boolean; hideWhenEmpty?: boolean }>(), {
  popperOptions: () => ({}),
  persistent: false,
  /* 非必要不开启，调试时可临时开启 */
  hideWhenEmpty: false,
})

const dropdownRef = ref<DropdownInstance>()

const slots = defineSlots<{
  /** 下拉触发器，必须只渲染一个有效根节点 */
  default(): unknown
  dropdown(): unknown
}>()

// 只展开标准菜单和 Fragment；业务 Action 仍按组件 VNode 判断。
function hasDropdownContent(children: unknown): boolean {
  const childNodes = Array.isArray(children) ? children : [children]
  return childNodes.some((child) => {
    if (isVNode(child)) {
      if (child.type === Fragment) return hasDropdownContent(child.children)
      if (child.type === MkDropdownMenu) {
        const menuSlots = child.children
        const menuSlot = menuSlots && typeof menuSlots === 'object' && 'default' in menuSlots ? menuSlots.default : undefined
        return hasDropdownContent(typeof menuSlot === 'function' ? menuSlot() : menuSlots)
      }
    }
    return hasRenderableSlotContent(child)
  })
}

function handleOpen() {
  dropdownRef.value?.handleOpen()
}

function handleClose() {
  dropdownRef.value?.handleClose()
}

defineExpose({ handleOpen, handleClose })
</script>

<template>
  <el-dropdown
    v-if="!hideWhenEmpty || hasDropdownContent(slots.dropdown?.())"
    class="mk-dropdown"
    ref="dropdownRef"
    :persistent="persistent"
    v-bind="$attrs"
  >
    <slot />
    <template #dropdown>
      <slot name="dropdown" />
    </template>
  </el-dropdown>
</template>
