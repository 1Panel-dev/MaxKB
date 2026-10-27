<script setup lang="ts">
defineOptions({ name: 'MarkdownQuickQuestion' })

defineProps<{
  question: string
  sendMessage?: (question: string) => void
}>()
</script>

<template>
  <!-- 发送快捷问题 -->
  <div
    class="quick-question mt-2 w-fit max-w-full rounded-lg border border-N300 bg-white px-3 py-1.5 leading-5 break-all"
    :class="sendMessage ? 'cursor-pointer hover:bg-N100' : 'text-N500'"
    @click="sendMessage?.(question)"
  >
    {{ question }}
  </div>
</template>
