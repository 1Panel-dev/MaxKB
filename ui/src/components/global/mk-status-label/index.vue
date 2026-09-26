<script setup lang="ts">
import { computed } from 'vue'
import { STATE_LABELS } from '@/constants/state'
import { STATE_TYPES } from '@/api/enums'
import type { State } from '@/api/types'

defineOptions({ name: 'MkStatusLabel' })

const props = withDefaults(
  defineProps<{
    active?: boolean // 启用状态
    activeText?: string
    inactiveText?: string
    status?: State // 多种状态
  }>(),
  { activeText: '已启用', inactiveText: '已禁用' },
)

/* 状态文案与 STATE_LABELS 共用状态键，兼容原有启用/禁用展示。 */
const statusOptions: Partial<Record<State, { name?: string; loading?: boolean }>> = {
  [STATE_TYPES.SUCCESS]: { name: 'icon_succeed_colorful' },
  [STATE_TYPES.FAILURE]: { name: 'icon_close_colorful' },
  [STATE_TYPES.STARTED]: { loading: true },
  [STATE_TYPES.REVOKE]: { loading: true },
  [STATE_TYPES.PENDING]: { loading: true },
  [STATE_TYPES.REVOKED]: { name: 'icon_close_colorful' },
}
const presentation = computed(() => {
  if (props.status !== undefined) return statusOptions[props.status]
  return props.active ? statusOptions[STATE_TYPES.SUCCESS] : undefined
})
const label = computed(() =>
  props.status !== undefined ? (STATE_LABELS[props.status] ?? props.status) : props.active ? props.activeText : props.inactiveText,
)
</script>

<template>
  <span class="flex-align-center gap-2">
    <LoadingIcon v-if="presentation?.loading" :size="16" />
    <MkIcon v-else-if="presentation?.name" :name="presentation.name" />
    <MkIcon v-else-if="status === undefined && !active" name="icon_ban_filled" class="text-N500!" />
    <span>{{ label }}</span>
  </span>
</template>
