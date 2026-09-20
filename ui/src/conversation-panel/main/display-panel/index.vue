<template>
  <!-- 只显示变体:仅 message-list,无 header、无 message-input(不发起对话)。
       里面的 form 拿不到发送能力时自动只读。 -->
  <main class="main-panel display-panel">
    <MessageList :app-name="list.appInfo.value?.name || 'AI 助手'" />
  </main>
</template>

<script setup lang="ts">
import MessageList from '../../components/message-list/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'

const list = useConversationListStore()
</script>

<style scoped lang="scss">
.main-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
  background: var(--bg, #fff);
  overflow: hidden;
  position: relative;
}
</style>
