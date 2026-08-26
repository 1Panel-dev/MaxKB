<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
defineProps<{
  label: MkDynamicFormValue
}>()
</script>

<template>
  <div class="flex align-center" style="display: inline-flex">
    <div class="flex-between mr-4">
      <span>{{ label.label }}</span>
    </div>
    <el-tooltip v-if="label.attrs.tooltip" effect="dark" placement="right">
      <template #content
        ><div style="max-width: 200px">{{ label.attrs.tooltip }}</div></template
      >
      <MkIcon name="icon_warning_filled" class="app-warning-icon" style="flex-shrink: 0"></MkIcon>
    </el-tooltip>
  </div>
</template>
