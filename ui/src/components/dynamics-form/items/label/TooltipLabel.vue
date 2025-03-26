<template>
  <div class="flex align-center" style="display: inline-flex">
    <div class="flex-between mr-4">
      <span>{{ label }}</span>
    </div>
    <el-tooltip effect="dark" placement="right">
      <template #content
        ><div style="max-width: 200px">{{ tooltip }}</div></template
      >
      <AppIcon iconName="app-warning" class="app-warning-icon" style="flex-shrink: 0"></AppIcon>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
defineProps<{
  label: string
  tooltip: string
}>()
</script>
<style lang="scss" scoped></style>
