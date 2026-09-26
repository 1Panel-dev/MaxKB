<script setup lang="ts">
import type { TableFilterOption } from './types'

defineOptions({ name: 'TableFilterSingle' })

defineProps<{
  modelValue: TableFilterOption['value'] | null | undefined
  options: TableFilterOption[]
  active: boolean
  width?: string | number
}>()
const emit = defineEmits<{ select: [value: TableFilterOption['value'] | null]; open: [] }>()
defineSlots<{ default(): unknown }>()

function handleVisibleChange(visible: boolean) {
  if (visible) emit('open')
}
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-start" :max-height="280" @visible-change="handleVisibleChange">
    <slot />
    <template #dropdown>
      <MkDropdownMenu :style="{ width: typeof width === 'number' ? `${width}px` : width }">
        <MkDropdownItem selectable :selected="!active" @click="emit('select', null)">全部</MkDropdownItem>
        <template v-for="option in options" :key="`${typeof option.value}:${option.value}`">
          <MkDropdownItem
            selectable
            :selected="active && modelValue === option.value"
            :disabled="option.disabled"
            @click="emit('select', option.value)"
          >
            <span class="min-w-0 truncate" :title="option.label">{{ option.label }}</span>
          </MkDropdownItem>
        </template>
      </MkDropdownMenu>
    </template>
  </MkDropdown>
</template>
