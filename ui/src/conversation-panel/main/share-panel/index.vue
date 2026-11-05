<script setup lang="ts">
import { provide } from 'vue'
import ShareMessageList from '../../components/share-message-list/index.vue'
import { SHARE_MESSAGE_LIST_KEY } from '../../components/share-message-list/index'
import { useSharePanelStore } from './index'

defineOptions({ name: 'SharePanel' })

const { title, messageList } = useSharePanelStore()
provide(SHARE_MESSAGE_LIST_KEY, messageList)
</script>

<template>
  <!-- 分享主面板：标题栏 + 只读分享消息列表 -->
  <main class="mk-conversation-main">
    <header class="mk-conversation-chat-header flex-align-center gap-3 p-4">
      <div class="min-w-0 flex-1">
        <h4 class="truncate">{{ title }}</h4>
      </div>
    </header>
    <ShareMessageList />
  </main>
</template>
