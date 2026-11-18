<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { StatusLabelType } from './types'

defineOptions({ name: 'MkStatusLabel' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  type?: StatusLabelType
  label?: string
  active?: boolean
  activeText?: string
  inactiveText?: string
  icon?: string
}>()

const displayType = computed(() => props.type ?? (props.active ? 'success' : 'disabled'))
const displayLabel = computed(() =>
  props.type !== undefined
    ? props.label
    : props.active
      ? (props.activeText ?? t('common.status.enabled'))
      : (props.inactiveText ?? t('common.status.disabled')),
)
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
