<script setup lang="ts">
import { computed, provide, ref } from 'vue'
import { EXPORT_MESSAGE_ELEMENT_KEY } from '../../components/header/header-actions/export/context.ts'
import ChatHeader from '../../components/header/chat/index.vue'
import MessageList from '../../components/message-list/index.vue'
import MessageInput from '../../components/message-input/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
import { useMessageInputStore } from '../../components/message-input/index'

const mainRef = ref<HTMLElement>()
provide(EXPORT_MESSAGE_ELEMENT_KEY, () => mainRef.value?.querySelector<HTMLElement>('.mk-conversation-content') ?? null)
const list = useConversationListStore()
const input = useMessageInputStore()
// 拖拽到面板任意处 → 交给 message-input 接收文件
const handleDrop = (e: DragEvent) => input.addFiles(e.dataTransfer?.files)
// 开启免责声明时在输入框下方居中显示，与显示设置预览一致
const disclaimerText = computed(() => (list.appInfo.value?.disclaimer ? list.appInfo.value.disclaimer_value : ''))
</script>
<template>
  <!-- 带输入框的主面板:header + message-list + message-input -->
  <main ref="mainRef" class="mk-conversation-main" @drop.prevent="handleDrop" @dragover.prevent>
    <!-- 头部可被替换(如 debug 用 debug header);默认普通 chat header -->
    <slot name="header">
      <ChatHeader />
    </slot>
    <!-- 聊天背景铺满标题栏以下的消息区与输入区，与显示设置预览一致 -->
    <div
      class="flex-column min-h-0 flex-1 bg-cover bg-center"
      :style="{ backgroundImage: list.appInfo.value?.chat_background ? `url(${JSON.stringify(list.appInfo.value.chat_background)})` : undefined }"
    >
      <MessageList :key="list.currentChatId.value" :app-name="list.appInfo.value?.name || 'AI 助手'"></MessageList>

      <footer v-if="!list.isShared.value" class="mk-conversation-content flex-col-center shrink-0 gap-2 p-4">
        <MessageInput />
        <p v-if="disclaimerText" class="wrap-anywhere text-center text-sm text-N500 -mb-1">{{ disclaimerText }}</p>
      </footer>
    </div>
  </main>
</template>
