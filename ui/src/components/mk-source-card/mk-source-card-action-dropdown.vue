<script setup lang="ts">
defineOptions({ name: 'MkSourceCardActionDropdown' })

defineSlots<{
  default: () => unknown
}>()
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-end" :teleported="false">
    <el-button class="-mb-[2px] -mr-1" text>
      <MkIcon name="icon_more_outlined" />
    </el-button>

    <template #dropdown>
      <MkDropdownMenu>
        <slot />
      </MkDropdownMenu>
    </template>
  </MkDropdown>
</template>
