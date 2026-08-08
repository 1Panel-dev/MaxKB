<script setup lang="ts">
import { ref } from 'vue'
import type { DropdownInstance } from 'element-plus'
import type { Options } from '@popperjs/core'

defineOptions({ name: 'MkDropdown', inheritAttrs: false })

withDefaults(
  defineProps<{
    popperOptions?: Partial<Options>
    persistent?: boolean
  }>(),
  {
    popperOptions: () => ({}),
    persistent: false,
    /* 非必要不开启，调试时可临时开启 */
  },
)

const dropdownRef = ref<DropdownInstance>()

defineSlots<{
  /** 下拉触发器，必须只渲染一个有效根节点 */
  default(): unknown
  dropdown(): unknown
}>()

function handleOpen() {
  dropdownRef.value?.handleOpen()
}

function handleClose() {
  dropdownRef.value?.handleClose()
}

defineExpose({ handleOpen, handleClose })
</script>

<template>
  <el-dropdown class="mk-dropdown" ref="dropdownRef" :persistent="persistent" v-bind="$attrs">
    <slot />
    <template #dropdown>
      <slot name="dropdown" />
    </template>
  </el-dropdown>
</template>
