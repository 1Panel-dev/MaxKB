<script setup lang="ts">
import { computed, type Component } from 'vue'
import { STATE_LABELS } from '@/constants/state'
import { STATE_TYPES } from '@/api/enums'
import type { State } from '@/api/types'
import { SuccessFilled, CircleCloseFilled, Loading } from '@element-plus/icons-vue'

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
const statusOptions: Partial<Record<State, { icon?: Component; className: string }>> = {
  [STATE_TYPES.SUCCESS]: { icon: SuccessFilled, className: 'text-success!' },
  [STATE_TYPES.FAILURE]: { icon: CircleCloseFilled, className: 'text-danger!' },
  [STATE_TYPES.STARTED]: { icon: Loading, className: 'is-loading' },
  [STATE_TYPES.REVOKE]: { icon: Loading, className: 'is-loading' },
  [STATE_TYPES.PENDING]: { icon: Loading, className: 'is-loading' },
  [STATE_TYPES.REVOKED]: { icon: CircleCloseFilled, className: 'text-danger!' },
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
    <MkIcon v-if="presentation?.icon" :icon="presentation.icon" :class="presentation.className" />
    <MkIcon v-else-if="status === undefined && !active" name="icon_ban_filled" class="text-N500!" />
    <span>{{ label }}</span>
  </span>
</template>
