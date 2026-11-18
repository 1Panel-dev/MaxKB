<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ParagraphMoveDirection } from './types'

defineOptions({ name: 'MoveParagraphAction' })
const { t } = useI18n({ useScope: 'global' })
defineProps<{ label: string; disabled?: boolean }>()
const emit = defineEmits<{ move: [direction: ParagraphMoveDirection]; 'visible-change': [visible: boolean] }>()

const positionOptions = [
  { labelKey: 'knowledge.paragraph.position.top', value: 'top' },
  { labelKey: 'knowledge.paragraph.position.up', value: 'up' },
  { labelKey: 'knowledge.paragraph.position.down', value: 'down' },
  { labelKey: 'knowledge.paragraph.position.bottom', value: 'bottom' },
] as const satisfies readonly { labelKey: string; value: ParagraphMoveDirection }[]
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
              {{ t(positionOption.labelKey) }}
            </MkDropdownItem>
          </template>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
