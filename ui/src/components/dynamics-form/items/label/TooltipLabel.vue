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
<style lang="scss" scope>
.aiMode-param-dialog {
  padding: 8px 8px 24px 8px;

  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }

  .el-dialog__body {
    padding: 16px !important;
  }

  .dialog-max-height {
    height: 550px;
  }

  .custom-slider {
    .el-input-number.is-without-controls .el-input__wrapper {
      padding: 0 !important;
    }
  }
}
</style>
