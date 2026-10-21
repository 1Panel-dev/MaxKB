<script setup lang="ts">
import { computed } from 'vue'
import type { StatusLabelType } from './types'

defineOptions({ name: 'MkStatusLabel' })

const props = withDefaults(
  defineProps<{
    type?: StatusLabelType
    label?: string
    active?: boolean
    activeText?: string
    inactiveText?: string
    icon?: string
  }>(),
  { activeText: '已启用', inactiveText: '已禁用' },
)

const displayType = computed(() => props.type ?? (props.active ? 'success' : 'disabled'))
const displayLabel = computed(() => (props.type !== undefined ? props.label : props.active ? props.activeText : props.inactiveText))
const iconName = computed(() => {
  if (props.icon) return props.icon
  if (displayType.value === 'custom') return undefined
  if (displayType.value === 'success') return 'icon_succeed_colorful'
  if (displayType.value === 'failure') return 'icon_close_colorful'
  return 'icon_ban_filled'
})
</script>

<template>
  <span class="flex-align-center gap-2">
    <LoadingIcon v-if="displayType === 'loading' && !icon" :size="16" />
    <MkIcon v-else-if="iconName" :name="iconName" :class="{ 'text-N500!': displayType === 'disabled' }" />
    <span>{{ displayLabel }}</span>
  </span>
</template>
