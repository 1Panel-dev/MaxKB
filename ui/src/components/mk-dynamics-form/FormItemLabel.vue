<script setup lang="ts">
import type { FormField } from './type'

defineOptions({ name: 'MkDynamicsFormItemLabel' })

defineProps<{
  formField: FormField
}>()
</script>

<template>
  {{ formField.label }}
</template>
