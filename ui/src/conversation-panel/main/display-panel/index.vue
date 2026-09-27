<script setup lang="ts">
import MessageList from '../../components/message-list/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'

const list = useConversationListStore()
</script>
<template>
  <!-- 只显示变体:仅 message-list,无 header、无 message-input(不发起对话)。
       里面的 form 拿不到发送能力时自动只读。 -->
  <main class="mk-conversation-main">
    <MessageList :app-name="list.appInfo.value?.name || 'AI 助手'" />
  </main>
</template>
