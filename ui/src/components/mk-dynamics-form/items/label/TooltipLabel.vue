<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
defineProps<{
  label: DynamicFormValue
}>()
</script>

<template>
  <div class="inline-flex items-center gap-2">
    <span>{{ label.label }}</span>
    <el-tooltip v-if="label.attrs.tooltip" :content="label.attrs.tooltip" placement="right">
      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
    </el-tooltip>
  </div>
</template>
