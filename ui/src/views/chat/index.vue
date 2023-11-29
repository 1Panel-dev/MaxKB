<template>
  <div class="chat">
    <div class="chat__header">
      <div class="chat-width"><h2 class="ml-24">111</h2></div>
    </div>
    <div class="chat__main chat-width"><AiDialog></AiDialog></div>
  </div>
</template>
<script setup lang="ts">
import AiDialog from '@/components/ai-dialog/index.vue'
</script>
<style lang="scss" scoped>
.chat {
  background-color: var(--app-layout-bg-color);
  &__header {
    background: var(--app-header-bg-color);
    position: fixed;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 100;
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    padding: var(--app-header-padding);
  }
  &__main {
    padding-top: calc(var(--app-header-height) + 24px);
    height: calc(100vh - var(--app-header-height) - 24px);
  }
  .chat-width {
    width: 840px;
    margin: 0 auto;
  }
}
</style>
