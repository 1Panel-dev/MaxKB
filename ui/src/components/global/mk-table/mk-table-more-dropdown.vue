<script setup lang="ts">
defineOptions({ name: 'MkTableMoreDropdown', inheritAttrs: false })

defineProps<{
  menuClass?: string
}>()

defineSlots<{
  /** 表格 More 菜单项，仅使用 MkDropdownItem */
  default(): unknown
}>()
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-end" v-bind="$attrs">
    <el-button aria-label="更多操作" type="primary" text @click.stop>
      <MkIcon name="icon_more_outlined" />
    </el-button>

    <template #dropdown>
      <MkDropdownMenu :class="menuClass">
        <slot />
      </MkDropdownMenu>
    </template>
  </MkDropdown>
</template>
