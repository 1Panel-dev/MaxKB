<template>
  <div class="content-failure mb-8">
    <span class="failure-icon">⚠️</span>
    <span>{{ content.content }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ content: any }>()
</script>
