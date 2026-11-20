<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import ConversationChat from '@/conversation-panel/view/chat/index.vue'
import ConversationEmbed from '@/conversation-panel/view/embed/index.vue'
import NoService from '@/views/chat/error/NoService.vue'
import { useStore } from '@/stores/chat'

defineOptions({ name: 'ChatApplication' })

// 单应用对话：智能体 ID 与会话地址同步由对话面板 chat 模式处理，页面只加载侧栏所需的当前用户
const { auth, user } = useStore()
const route = useRoute()
const unavailable = computed(() => auth.unavailablePath === route.fullPath)
// 嵌入脚本以 iframe 打开 `?mode=embed`，使用嵌入头部；会话地址同步保留该参数
const isEmbed = computed(() => route.query.mode === 'embed')

// 当前用户随 token 变化：认证 Store 切换 token 时会清除用户档案，这里重新加载
watch(
  [() => auth.token, unavailable],
  ([token, serviceUnavailable]) => {
    if (!serviceUnavailable && token && !user.chatUserProfile) user.loadCurrentUser()
  },
  { immediate: true },
)
</script>

<template>
  <NoService v-if="unavailable" />
  <main v-else class="h-screen bg-white">
    <!-- token 变化（重新认证或登录）时重建面板，重新加载智能体与会话数据；token 清除后等待重新认证 -->
    <template v-if="auth.token">
      <ConversationEmbed v-if="isEmbed" :key="auth.token" />
      <ConversationChat v-else :key="auth.token" />
    </template>
  </main>
</template>
