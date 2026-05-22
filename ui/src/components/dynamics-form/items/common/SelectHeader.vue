<template>
  <div
    v-if="header"
    style="font-size: 13px; color: #1f2329; padding: 2px 4px; display: flex; align-items: center"
  >
    <span>{{ header.label }}</span>
    <span v-if="header.required" style="color: #f54a45; margin-left: 4px">*</span>
    <el-tooltip v-if="header.tooltip" effect="dark" placement="right">
      <template #content>
        <div style="max-width: 200px">{{ header.tooltip }}</div>
      </template>
      <AppIcon
        iconName="app-warning"
        class="app-warning-icon"
        style="margin-left: 4px; flex-shrink: 0"
      ></AppIcon>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
defineProps<{
  header: any
}>()
</script>
<style lang="scss">
.el-select-dropdown__header {
  border-bottom: none;
  padding: 4px 8px 0;
}
</style>
