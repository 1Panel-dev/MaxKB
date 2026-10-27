<script setup lang="ts">
import MarkdownRenderer from '../../markdown-renderer/index.vue'

defineOptions({ name: 'ConversationTextContent' })

defineProps<{
  content: { content?: string | null }
}>()
</script>

<template>
  <!-- 正文兼容 v2 标签（快捷问题、HTML、图表等），其余按 Markdown 渲染 -->
  <div class="mk-conversation-text-content">
    <MarkdownRenderer :source="content.content ?? ''" />
  </div>
</template>
