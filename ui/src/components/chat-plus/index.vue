<template>
  <div class="chat-plus" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- 侧边栏 -->
    <div class="chat-plus__sidebar" :class="{ open: sidebarOpen }">
      <slot name="sidebar" v-bind="sidebarSlotProps">
        <ConversationList
          :conversations="chat.conversations.value"
          :current-id="chat.currentChatId.value"
          :is-open="sidebarOpen"
        />
      </slot>
    </div>

    <!-- 遮罩 -->
    <div v-if="sidebarOpen && isMobile" class="chat-plus__mask" @click="sidebarOpen = false" />

    <!-- 对话区 -->
    <div class="chat-plus__main">
      <ChatPanel
        ref="panelRef"
        :messages="chat.messages.value"
        :loading="chat.msgLoading.value"
        :stream-loading="chat.streamLoading.value"
        @send="handleSend"
        @stop="chat.stopStream()"
        @toggle="sidebarOpen = !sidebarOpen"
        @scroll="handleScroll"
      >
        <!-- Header 插槽 -->
        <template #header>
          <slot name="header" />
        </template>

        <!-- 消息渲染插槽 -->
        <template #message="{ message, index }">
          <slot name="message" :message="message" :index="index">
            <div v-if="message.role === 'USER'" class="msg-user">
              <div class="msg-user-text">{{ getUserText(message) }}</div>
            </div>
            <div v-else class="msg-assistant">
              <ContentItem
                v-for="(block, bi) in message.content"
                :key="bi"
                :content="block"
              />
            </div>
          </slot>
        </template>

        <!-- 空态插槽 -->
        <template #empty>
          <slot name="empty">
            <div class="default-empty">
              <p class="empty-title">AI 助手</p>
              <p class="empty-sub">有什么可以帮你的？</p>
            </div>
          </slot>
        </template>

        <!-- Loading 插槽 -->
        <template #loading>
          <slot name="loading">
            <div class="default-loading"><span></span><span></span><span></span></div>
          </slot>
        </template>

        <!-- 输入框插槽 -->
        <template #input>
          <slot name="input" :send="handleSend" :loading="chat.streamLoading.value">
            <div class="default-input">
              <textarea
                ref="inputRef"
                v-model="inputText"
                :disabled="chat.streamLoading.value"
                :placeholder="chat.streamLoading.value ? '正在回复中...' : '输入消息...'"
                @keydown="onKeydown"
                rows="1"
              />
              <button
                v-if="!chat.streamLoading.value"
                class="send-btn"
                :class="{ active: canSend }"
                :disabled="!canSend"
                @click="send"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 14V2M3 7l5-5 5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button v-else class="send-btn stop" @click="chat.stopStream()">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <rect x="2" y="2" width="10" height="10" rx="2" fill="currentColor"/>
                </svg>
              </button>
            </div>
          </slot>
        </template>
      </ChatPanel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, provide } from 'vue'
import { chatBus, ChatEvents } from './bus'
import { useChat } from './composable'
import { type ChatType } from './api'
import ChatPanel from './component/chat-panel/index.vue'
import ConversationList from './component/conversation-list/index.vue'
import ContentItem from './component/answer-content/items/index.vue'

const props = withDefaults(
  defineProps<{
    type?: ChatType
    applicationId?: string
    applicationDetails?: any
  }>(),
  {
    type: 'CHAT',
  },
)

const emit = defineEmits<{
  openChat: [chatId: string]
  refresh: [chatId: string]
}>()

const resolvedAppId = computed(() => props.applicationId || props.applicationDetails?.id)
const chat = useChat(props.type, resolvedAppId)

const panelRef = ref()
const inputRef = ref()
const inputText = ref('')
const sidebarOpen = ref(false)
const isMobile = ref(window.innerWidth < 768)

const canSend = computed(() => inputText.value.trim() && !chat.streamLoading.value)

const sidebarSlotProps = computed(() => ({
  conversations: chat.conversations.value,
  currentId: chat.currentChatId.value,
  open: (id: string) => handleOpenChat(id),
  create: () => handleNewChat(),
  remove: (id: string) => chat.deleteChat(id),
  rename: (id: string, name: string) => chat.renameChat(id, name),
}))

// ── 操作 ───────────────────────────────────────────────
const handleNewChat = async () => {
  const chatId = await chat.openChat()
  sidebarOpen.value = false
  emit('openChat', chatId)
  return chatId
}

const handleOpenChat = async (id: string) => {
  await chat.switchChat(id)
  sidebarOpen.value = false
}

const handleSend = async (text: string) => {
  if (!text.trim() || chat.streamLoading.value) return

  if (!chat.currentChatId.value) {
    await handleNewChat()
  }

  // push 用户消息
  chat.pushMessage({
    role: 'USER',
    content: [{ type: 'TEXT', content: text }],
    id: '',
  })

  try {
    await chat.sendMessage(text)
    emit('refresh', chat.currentChatId.value)
  } catch {}

  nextTick(() => panelRef.value?.scrollToBottom())
}

const handleScroll = () => {
  // 分页加载更多
}

const getUserText = (msg: any) =>
  msg.content?.find((c: any) => c.type === 'TEXT')?.content || ''

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
    e.preventDefault()
    send()
  }
}

const send = () => {
  if (!canSend.value) return
  handleSend(inputText.value.trim())
  inputText.value = ''
}

// ── Bus 通知（仅用于通知，不传数据） ───────────────────
chatBus.on(ChatEvents.OPEN_CONVERSATION, (id: string) => handleOpenChat(id))
chatBus.on(ChatEvents.NEW_CONVERSATION, () => handleNewChat())
chatBus.on(ChatEvents.DELETE_CONVERSATION, (id: string) => chat.deleteChat(id))
chatBus.on(ChatEvents.RENAME_CONVERSATION, (id: string, name: string) => chat.renameChat(id, name))

// ── 生命周期 ───────────────────────────────────────────
const onResize = () => { isMobile.value = window.innerWidth < 768 }

onMounted(() => {
  window.addEventListener('resize', onResize)
  if (props.type === 'CHAT') {
    chat.loadConversations()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chatBus.clear()
})

provide('chat', chat)
</script>
<style lang="scss">
@use './index.scss';
</style>
