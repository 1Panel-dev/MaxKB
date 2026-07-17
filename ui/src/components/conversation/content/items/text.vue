<template>
  <div class="content-text">
    <MdPreview editorId="conversation-text" :modelValue="content.content || ''" />
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
.content-text :deep(.md-editor) {
  background: transparent;
}
</style>
