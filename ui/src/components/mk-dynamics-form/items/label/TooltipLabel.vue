<template>
  <div class="flex align-center" style="display: inline-flex">
    <div class="flex-between mr-4">
      <span>{{ label.label }}</span>
    </div>
    <el-tooltip v-if="label.attrs.tooltip" effect="dark" placement="right">
      <template #content
        ><div style="max-width: 200px">{{ label.attrs.tooltip }}</div></template
      >
      <AppIcon iconName="app-warning" class="app-warning-icon" style="flex-shrink: 0"></AppIcon>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
defineProps<{
  label: any
}>()
</script>
<style lang="scss" scoped></style>
