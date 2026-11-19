<script setup lang="ts">
import { computed, provide } from 'vue'
import { SHARE_MESSAGE_LIST_KEY } from '../../components/share-message-list/index'
import ShareMessageList from '../../components/share-message-list/index.vue'
import { useSharePanelStore } from './index'
import { resetUrl } from '@/utils/icon'

defineOptions({ name: 'SharePanel' })

const { title, appInfo, messageList } = useSharePanelStore()
const chatBackground = computed(() => resetUrl(appInfo.value?.chat_background))
provide(SHARE_MESSAGE_LIST_KEY, messageList)
</script>

<template>
  <!-- 分享主面板：标题栏 + 只读分享消息列表 -->
  <main
    class="mk-conversation-main bg-cover! bg-center!"
    :style="{ backgroundImage: chatBackground ? `url(${JSON.stringify(chatBackground)})` : undefined }"
  >
    <header class="mk-conversation-chat-header flex-align-center gap-3 p-4">
      <div class="min-w-0 flex-1">
        <h4 class="truncate">{{ title }}</h4>
      </div>
    </header>
    <ShareMessageList />
  </main>
</template>
