<script setup lang="ts">
import type { FormField } from '@/components/mk-dynamics-form/type'
defineProps<{
  // 表单Item
  formField: FormField
}>()
</script>

<template>
  {{ formField.label }}
</template>
