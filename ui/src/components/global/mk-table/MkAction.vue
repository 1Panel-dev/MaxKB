<script setup lang="ts">
defineOptions({ name: 'MkAction', inheritAttrs: false })
withDefaults(defineProps<{ display?: 'menu' | 'button'; label: string; icon: string; disabled?: boolean; divided?: boolean }>(), { display: 'menu' })
const emit = defineEmits<{ click: [event: MouseEvent] }>()
</script>

<template>
  <!-- 菜单操作 -->
  <MkDropdownItem v-if="display === 'menu'" v-bind="$attrs" :disabled="disabled" :divided="divided" @click.stop="emit('click', $event)">
    <template #icon><MkIcon :name="icon" /></template>
    {{ label }}
  </MkDropdownItem>
  <MkTooltip v-else :content="label" placement="top">
    <!-- 图标操作 -->
    <el-button v-bind="$attrs" text type="primary" :disabled="disabled" @click.stop="emit('click', $event)">
      <MkIcon :name="icon" />
    </el-button>
  </MkTooltip>
</template>
