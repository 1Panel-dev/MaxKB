<template>
  {{ formField.label }}
</template>
<script setup lang="ts">
import type { FormField } from '@/components/dynamics-form/type'
const props = defineProps<{
  // 表单Item
  formField: FormField
}>()
</script>
<style lang="scss" scoped></style>
