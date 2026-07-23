<script setup lang="ts">
defineOptions({ inheritAttrs: false })

defineSlots<{
  /** 菜单项，仅使用 MkDropdownItem */
  default(): unknown
}>()
</script>

<template>
  <el-dropdown-menu v-bind="$attrs">
    <slot />
  </el-dropdown-menu>
</template>
