<script setup lang="ts">
import ChatHeader from '../../components/header/chat/index.vue'
import MessageList from '../../components/message-list/index.vue'
import MessageInput from '../../components/message-input/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
import { useMessageInputStore } from '../../components/message-input/index'
import { usePortalConversationListStore } from '../../left-sidebar/portal-conversation-list/index'

defineOptions({ name: 'PortalChatPanel' })

const list = useConversationListStore()
const input = useMessageInputStore()
const portalList = usePortalConversationListStore()

// 拖拽到面板任意处 → 交给 message-input 接收文件
const handleDrop = (e: DragEvent) => input.addFiles(e.dataTransfer?.files)
</script>
<template>
  <!-- 门户对话主面板:header + message-list + message-input -->
  <main class="mk-conversation-main" @drop.prevent="handleDrop" @dragover.prevent>
    <!-- 收起侧栏时标题栏的新建对话与侧栏一致：没有当前智能体时选择智能体 -->
    <ChatHeader :new-conversation="portalList.newConversation" />
    <MessageList v-if="portalList.currentApplicationId.value" :app-name="list.appInfo.value?.name || 'AI 助手'" />
    <!-- 未确定智能体时不显示欢迎语：分组加载完成且没有可用智能体时显示空状态 -->
    <div v-else class="flex-center min-h-0 flex-1">
      <MkEmpty v-if="portalList.isApplicationGroupsLoaded.value" description="暂无可用智能体" />
    </div>
    <footer class="flex-center shrink-0 p-4"><MessageInput /></footer>
  </main>
</template>
