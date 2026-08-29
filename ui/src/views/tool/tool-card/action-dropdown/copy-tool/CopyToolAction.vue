<script setup lang="ts">
import type { ToolItem } from '@/api/types'

defineOptions({ name: 'CopyToolAction' })

const props = defineProps<{
  label: string
  tool: ToolItem
}>()

const emit = defineEmits<{
  copy: [tool: ToolItem]
}>()
</script>

<template>
  <MkDropdownItem @click="emit('copy', props.tool)">
    <template #icon><MkIcon name="icon_copy_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
