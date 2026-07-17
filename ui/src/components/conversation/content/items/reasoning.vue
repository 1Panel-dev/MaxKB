<template>
  <div class="content-reasoning" v-if="content.content?.trim()">
    <div class="reasoning-header" @click="expanded = !expanded">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" :class="{ rotated: expanded }">
        <path d="M5 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>Reasoning</span>
    </div>
    <div v-show="expanded" class="reasoning-content">
      <MdPreview editorId="reasoning-text" :modelValue="content.content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

defineProps<{
  content: any
}>()

const expanded = ref(false)
</script>

<style scoped>
.content-reasoning {
  background: var(--bg2, #fafafa);
  border: 1px solid var(--bd, #dcdfe6);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 8px;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
  color: var(--t2, #606266);
  user-select: none;
}

.reasoning-header svg {
  transition: transform 0.2s;
}

.reasoning-header svg.rotated {
  transform: rotate(90deg);
}

.reasoning-content {
  padding: 0 12px 12px;
  font-size: 13px;
}

.reasoning-content :deep(.md-editor) {
  background: transparent;
}
</style>
