<script setup lang="ts">
import { SuccessFilled } from '@element-plus/icons-vue'

defineOptions({ name: 'MkStatusLabel' })

withDefaults(defineProps<{ active: boolean; activeText?: string; inactiveText?: string }>(), { activeText: '已启用', inactiveText: '已禁用' })
</script>

<template>
  <span class="flex items-center gap-2">
    <MkIcon v-if="active" :icon="SuccessFilled" class="text-success!" />
    <MkIcon v-else name="icon_ban_filled" class="text-N500!" />
    <span>{{ active ? activeText : inactiveText }}</span>
  </span>
</template>
