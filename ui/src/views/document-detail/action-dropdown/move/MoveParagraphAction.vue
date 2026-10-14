<script setup lang="ts">
import type { ParagraphMoveDirection } from './types'

defineOptions({ name: 'MoveParagraphAction' })
defineProps<{ label: string; disabled?: boolean }>()
const emit = defineEmits<{ move: [direction: ParagraphMoveDirection]; 'visible-change': [visible: boolean] }>()

const positionOptions = [
  { label: '置于顶部', value: 'top' },
  { label: '上移', value: 'up' },
  { label: '下移', value: 'down' },
  { label: '置于底部', value: 'bottom' },
] as const satisfies readonly { label: string; value: ParagraphMoveDirection }[]
</script>

<template>
  <!-- 展开分段位置菜单 -->
  <MkDropdownItem class="p-0!" @click.prevent.stop>
    <MkDropdown class="w-full" trigger="hover" placement="left-start" @visible-change="emit('visible-change', $event)">
      <div class="flex-between w-full gap-2 p-2">
        <div class="flex-align-center gap-2">
          <MkIcon name="icon_drag_outlined" class="text-N600!" />
          <span>{{ label }}</span>
        </div>
        <MkIcon name="icon_right_outlined" class="text-N600!" />
      </div>
      <template #dropdown>
        <MkDropdownMenu>
          <template v-for="positionOption in positionOptions" :key="positionOption.value">
            <!-- 按所选方向移动分段 -->
            <MkDropdownItem :disabled="disabled" @click="emit('move', positionOption.value)">
              {{ positionOption.label }}
            </MkDropdownItem>
          </template>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
