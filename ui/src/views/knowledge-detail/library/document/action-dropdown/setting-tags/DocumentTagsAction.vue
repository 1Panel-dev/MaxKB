<script setup lang="ts">
defineOptions({ name: 'DocumentTagsAction' })
defineProps<{ label: string; icon?: string; disabled?: boolean }>()
</script>

<template>
  <!-- 文档标签设置入口 -->
  <MkAction :label="label" :icon="icon" :disabled="disabled" />
</template>
