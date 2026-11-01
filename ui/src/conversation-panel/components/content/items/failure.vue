<script setup lang="ts">
defineOptions({ name: 'ConversationFailureContent' })

defineProps<{
  content: { content?: string | null }
}>()
</script>

<template>
  <div class="flex-align-center gap-2">
    <MkIcon name="icon_warning_filled" class="text-danger!" />
    <span>{{ content.content || '发生错误' }}</span>
  </div>
</template>

<style scoped lang="scss"></style>
