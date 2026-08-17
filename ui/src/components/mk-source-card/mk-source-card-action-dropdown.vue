<script setup lang="ts">
defineOptions({ name: 'MkSourceCardActionDropdown' })

defineSlots<{
  default: () => unknown
}>()
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-end" :teleported="false">
    <el-button text>
      <MkIcon name="icon_more_outlined" />
    </el-button>

    <template #dropdown>
      <slot />
    </template>
  </MkDropdown>
</template>
