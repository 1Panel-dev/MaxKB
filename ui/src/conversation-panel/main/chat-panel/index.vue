<script setup lang="ts">
import ChatHeader from '../../components/header/chat/index.vue'
import MessageList from '../../components/message-list/index.vue'
import MessageInput from '../../components/message-input/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
import { useMessageInputStore } from '../../components/message-input/index'

const list = useConversationListStore()
const input = useMessageInputStore()

// 拖拽到面板任意处 → 交给 message-input 接收文件
const handleDrop = (e: DragEvent) => input.addFiles(e.dataTransfer?.files)
</script>
<template>
  <!-- 带输入框的主面板:header + message-list + message-input -->
  <main class="mk-conversation-main" @drop.prevent="handleDrop" @dragover.prevent>
    <!-- 头部可被替换(如 debug 用 debug header);默认普通 chat header -->
    <slot name="header"><ChatHeader /></slot>
    <MessageList :app-name="list.appInfo.value?.name || 'AI 助手'" />
    <footer class="flex-center shrink-0 p-4"><MessageInput /></footer>
  </main>
</template>
