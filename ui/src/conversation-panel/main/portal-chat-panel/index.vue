<script setup lang="ts">
import { computed, provide, ref } from 'vue'
import { EXPORT_MESSAGE_ELEMENT_KEY } from '../../components/header/header-actions/export/context.ts'
import { useShareLinkStoreOptional } from '../../components/message-list/share/index'
import PortalHeader from '../../components/header/portal/index.vue'
import MessageList from '../../components/message-list/index.vue'
import MessageInput from '../../components/message-input/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
import { useMessageInputStore } from '../../components/message-input/index'
import { usePortalConversationListStore } from '../../left-sidebar/portal-conversation-list/index'

defineOptions({ name: 'PortalChatPanel' })

const shareLink = useShareLinkStoreOptional()
const mainRef = ref<HTMLElement>()
provide(EXPORT_MESSAGE_ELEMENT_KEY, () => mainRef.value?.querySelector<HTMLElement>('.mk-conversation-content') ?? null)
const list = useConversationListStore()
const input = useMessageInputStore()
const portalList = usePortalConversationListStore()

// 拖拽到面板任意处 → 交给 message-input 接收文件
const handleDrop = (e: DragEvent) => input.addFiles(e.dataTransfer?.files)

// 当前智能体开启免责声明时在输入框下方居中显示，与显示设置预览一致
const disclaimerText = computed(() =>
  portalList.currentApplicationId.value && list.appInfo.value?.disclaimer ? list.appInfo.value.disclaimer_value : '',
)
</script>
<template>
  <!-- 门户对话主面板:header + message-list + message-input -->
  <main ref="mainRef" class="mk-conversation-main" @drop.prevent="handleDrop" @dragover.prevent>
    <!-- 收起侧栏时标题栏的新建对话与侧栏一致：没有当前智能体时选择智能体 -->
    <PortalHeader :new-conversation="portalList.newConversation" @share="shareLink?.enterShare()" />
    <MessageList :key="list.currentChatId.value" v-if="portalList.currentApplicationId.value" :app-name="list.appInfo.value?.name || 'AI 助手'" />
    <!-- 未确定智能体时不显示欢迎语：分组加载完成且没有可用智能体时显示空状态 -->
    <div v-else class="flex-center min-h-0 flex-1">
      <MkEmpty v-if="portalList.isApplicationGroupsLoaded.value" description="暂无可用智能体" />
    </div>
    <footer v-if="!list.isShared.value" class="mk-conversation-content flex-col-center shrink-0 gap-2 p-4">
      <MessageInput />
      <p v-if="disclaimerText" class="wrap-anywhere text-center text-sm text-N500 -mb-1">{{ disclaimerText }}</p>
    </footer>
  </main>
</template>
