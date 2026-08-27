<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
defineProps<{
  header: DynamicFormValue
}>()
</script>

<template>
  <div v-if="header">
    <span>{{ header.label }}</span>
    <span v-if="header.required" style="color: #f54a45; margin-left: 4px">*</span>
    <el-tooltip v-if="header.tooltip" effect="dark" placement="right">
      <template #content>
        <div>{{ header.tooltip }}</div>
      </template>
      <MkIcon
        name="icon_warning_filled"
        class="app-warning-icon"
        style="margin-left: 4px; flex-shrink: 0"
      ></MkIcon>
    </el-tooltip>
  </div>
</template>
<style lang="scss"></style>
