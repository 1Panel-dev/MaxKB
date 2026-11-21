<script setup lang="ts">
import { computed, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ParagraphMoveDirection } from './types'

defineOptions({ name: 'MoveParagraphAction' })
const { t } = useI18n({ useScope: 'global' })
defineProps<{ label: string; disabled?: boolean }>()
const emit = defineEmits<{ move: [direction: ParagraphMoveDirection]; 'visible-change': [visible: boolean] }>()

const positionOptions = reactive([
  { label: computed(() => t('knowledge.paragraph.position.top')), value: 'top' },
  { label: computed(() => t('knowledge.paragraph.position.up')), value: 'up' },
  { label: computed(() => t('knowledge.paragraph.position.down')), value: 'down' },
  { label: computed(() => t('knowledge.paragraph.position.bottom')), value: 'bottom' },
] as const) satisfies readonly { label: string; value: ParagraphMoveDirection }[]
</script>

<template>
  <!-- 展开分段位置菜单 -->
  <MkDropdownItem class="p-0!" @click.prevent.stop>
    <MkDropdown class="w-full" trigger="hover" placement="left-start" @visible-change="emit('visible-change', $event)">
      <div class="flex-between w-full gap-2 py-[5px] px-2">
        <div class="flex-align-center gap-2">
          <MkIcon name="icon_drag_outlined" class="text-N600!" />
          <span>{{ label }}</span>
        </div>
        <MkIcon name="icon_right_outlined" class="text-N500!" />
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
