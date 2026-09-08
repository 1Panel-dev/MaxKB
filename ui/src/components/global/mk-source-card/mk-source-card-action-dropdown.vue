<script setup lang="ts">
import { computed, useSlots } from 'vue'
import { hasRenderableSlotContent } from '@/utils/vnode'

defineOptions({ name: 'MkSourceCardActionDropdown' })

defineSlots<{ default: () => unknown }>()

const slots = useSlots()
const hasDropdownItems = computed(() => hasRenderableSlotContent(slots.default?.()))
</script>

<template>
  <MkDropdown v-if="hasDropdownItems" trigger="click" placement="bottom-end" persistent :teleported="false">
    <el-button class="-mb-[2px] -mr-1" text>
      <MkIcon name="icon_more_outlined" />
    </el-button>

    <template #dropdown>
      <MkDropdownMenu>
        <slot />
      </MkDropdownMenu>
    </template>
  </MkDropdown>
</template>
