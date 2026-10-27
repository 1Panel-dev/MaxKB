<script setup lang="ts">
defineOptions({ name: 'MarkdownQuickQuestion' })

defineProps<{
  question: string
  sendMessage?: (question: string) => void
}>()
</script>

<template>
  <!-- 发送快捷问题 -->
  <el-button size="large" class="mt-2 rounded-xl!" plain @click="sendMessage?.(question)">
    {{ question }}
  </el-button>
</template>
