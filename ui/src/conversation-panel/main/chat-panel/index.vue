<template>
  <!-- 带输入框的主面板:header + message-list + message-input -->
  <main class="main-panel" @drop.prevent="handleDrop" @dragover.prevent>
    <!-- 头部可被替换(如 debug 用 debug header);默认普通 chat header -->
    <slot name="header"><ChatHeader /></slot>
    <MessageList :app-name="list.appInfo.value?.name || 'AI 助手'" />
    <footer class="panel-input"><MessageInput /></footer>
  </main>
</template>

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
.panel-input {
  flex-shrink: 0;
  padding: 12px 16px 16px;
  background: var(--bg, #fff);
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
