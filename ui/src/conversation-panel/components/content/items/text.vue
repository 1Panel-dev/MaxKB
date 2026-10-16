<script setup lang="ts">
import { useId } from 'vue'

defineOptions({ name: 'ConversationTextContent' })

defineProps<{
  content: { content?: string | null }
}>()

const editorId = `conversation-text-${useId()}`
</script>

<template>
  <div class="mk-conversation-text-content">
    <MdPreview :editor-id="editorId" :model-value="content.content ?? ''" />
  </div>
</template>
