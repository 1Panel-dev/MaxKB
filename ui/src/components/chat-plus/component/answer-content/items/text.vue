<template>
  <div class="content-text-item">
    <MdPreview editorId="chat-plus-text" :modelValue="content.content || ''" />
  </div>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

defineProps<{
  content: any
}>()
</script>

<style scoped>
.content-text-item :deep(.md-editor) {
  background: transparent;
}
</style>
