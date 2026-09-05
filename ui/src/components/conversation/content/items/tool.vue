<template>
  <div class="content-tool">
    <div class="tool-header">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M10.5 2.5h-7a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1v-7a1 1 0 00-1-1z" stroke="currentColor" stroke-width="1.2"/>
        <path d="M5.5 5.5h3M5.5 8h3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      </svg>
      <span class="tool-name">{{ content.toolName || 'Tool' }}</span>
      <span v-if="content.status" class="tool-status" :class="content.status">
        {{ content.status }}
      </span>
    </div>
    <div v-if="content.content" class="tool-content">
      <MdPreview editorId="tool-text" :modelValue="content.content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

defineProps<{
  content: any
}>()
</script>

<style scoped lang="scss">
.content-tool {
  background: var(--bg2, #fafafa);
  border: 1px solid var(--bd, #dcdfe6);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 8px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 12px;
  color: var(--t2, #606266);
}

.tool-name {
  font-weight: 500;
}

.tool-status {
  margin-left: auto;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--hv, #f5f7fa);
}

.tool-status.success {
  color: #67c23a;
}

.tool-status.error {
  color: #f56c6c;
}

.tool-content {
  padding: 0 12px 12px;
  font-size: 13px;
}

.tool-content :deep(.md-editor) {
  background: transparent;
}
</style>
