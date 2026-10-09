<script setup lang="ts">
import { watch } from 'vue'
import ConversationChat from '@/conversation-panel/view/chat/index.vue'
import { useStore } from '@/stores/chat'

defineOptions({ name: 'ChatApplication' })

// 单应用对话：智能体 ID 与会话地址同步由对话面板 chat 模式处理，页面只加载侧栏所需的当前用户
const { auth, user } = useStore()

// 当前用户随 token 变化：认证 Store 切换 token 时会清除用户档案，这里重新加载
watch(
  () => auth.token,
  (token) => {
    if (token && !user.chatUserProfile) user.loadCurrentUser()
  },
  { immediate: true },
)
</script>

<template>
  <main class="h-screen bg-white">
    <!-- token 变化（重新认证或登录）时重建面板，重新加载智能体与会话数据；token 清除后等待重新认证 -->
    <ConversationChat v-if="auth.token" :key="auth.token" />
  </main>
</template>
