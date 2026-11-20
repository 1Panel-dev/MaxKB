<script setup lang="ts">
defineOptions({ name: 'MarkdownQuickQuestion' })

defineProps<{
  question: string
  sendMessage?: (question: string) => void
}>()
</script>

<template>
  <!-- 发送快捷问题 -->
  <el-button
    size="large"
    class="mk-conversation-export-include mt-2 h-auto! max-w-full whitespace-normal! rounded-xl! py-2!"
    plain
    @click="sendMessage?.(question)"
  >
    <span class="min-w-0 break-words text-left leading-[22px]">{{ question }}</span>
  </el-button>
</template>
