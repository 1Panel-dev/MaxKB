<script setup lang="ts">
import type { FormFieldLabel } from '../../type'

defineProps<{ label: FormFieldLabel; required: boolean }>()
</script>

<template>
  <div class="inline-flex items-center gap-2">
    <span :class="{ 'mk-required': required }">{{ label.label }}</span>
    <el-tooltip v-if="label.attrs?.tooltip" :content="label.attrs.tooltip" placement="right">
      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
    </el-tooltip>
  </div>
</template>
