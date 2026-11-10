<script setup lang="ts">
import MessageList from '../../components/message-list/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'

const list = useConversationListStore()
</script>
<template>
  <!-- 只显示变体:仅 message-list,无 header、无 message-input(不发起对话)。
       里面的 form 拿不到发送能力时自动只读。 -->
  <main class="mk-conversation-main">
    <!-- 聊天背景铺满消息区，与显示设置预览一致 -->
    <div
      class="flex-column min-h-0 flex-1 bg-cover bg-center"
      :style="{ backgroundImage: list.appInfo.value?.chat_background ? `url(${JSON.stringify(list.appInfo.value.chat_background)})` : undefined }"
    >
      <MessageList :key="list.currentChatId.value" :app-name="list.appInfo.value?.name || 'AI 助手'" />
    </div>
  </main>
</template>
