<script setup lang="ts">
import { ElTooltip } from 'element-plus'
import { TOOLTIP_SHOW_DELAY } from './constants'

defineOptions({ name: 'MkTooltip', inheritAttrs: false })

const props = withDefaults(defineProps<{ showAfter?: number }>(), { showAfter: TOOLTIP_SHOW_DELAY })

defineSlots<{ default(): unknown; content(): unknown }>()
</script>

<template>
  <ElTooltip v-bind="$attrs" :show-after="props.showAfter">
    <slot />
    <template v-if="$slots.content" #content>
      <slot name="content" />
    </template>
  </ElTooltip>
</template>
