<template>
  <div class="content-failure">
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M8 1.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM8 4v4M8 10.5h.006" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    </svg>
    <span>{{ content.content || '发生错误' }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  content: any
}>()
</script>

<style scoped lang="scss">
.content-failure {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #ef4444;
  font-size: 13px;
  line-height: 1.5;
}

.content-failure svg {
  flex-shrink: 0;
  margin-top: 1px;
}
</style>
