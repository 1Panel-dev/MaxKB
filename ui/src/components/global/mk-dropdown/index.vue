<script setup lang="ts">
import { computed, ref } from 'vue'
import type { DropdownInstance } from 'element-plus'
import type { Options } from '@popperjs/core'

defineOptions({ name: 'MkDropdown', inheritAttrs: false })

const props = withDefaults(
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

const mergedPopperOptions = computed<Partial<Options>>(() => ({
  ...props.popperOptions,
  modifiers: [
    ...(props.popperOptions.modifiers ?? []),
    { name: 'offset', options: { offset: [0, 4] } },
  ],
}))

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
    class="mk-dropdown"
    ref="dropdownRef"
    :persistent="persistent"
    v-bind="$attrs"
    :show-arrow="false"
    :popper-options="mergedPopperOptions"
  >
    <slot />
    <template #dropdown>
      <slot name="dropdown" />
    </template>
  </el-dropdown>
</template>
