<script setup lang="ts">
import { inject } from 'vue'
import { actionContextKey } from './context'

defineOptions({ name: 'MkAction', inheritAttrs: false })
defineProps<{ label: string; icon: string; disabled?: boolean; divided?: boolean }>()
const emit = defineEmits<{ click: [event: MouseEvent] }>()
const context = inject(actionContextKey, undefined)
</script>

<template>
  <!-- 菜单操作 -->
  <MkDropdownItem
    v-if="context?.display === 'menu'"
    v-bind="$attrs"
    :disabled="disabled"
    :divided="divided && !context.first"
    @click.stop="emit('click', $event)"
  >
    <template #icon><MkIcon :name="icon" /></template>
    {{ label }}
  </MkDropdownItem>
  <MkTooltip v-else :content="label" placement="top">
    <!-- 图标操作 -->
    <el-button v-bind="$attrs" type="primary" text :disabled="disabled" @click.stop="emit('click', $event)">
      <MkIcon :name="icon" />
    </el-button>
  </MkTooltip>
</template>
