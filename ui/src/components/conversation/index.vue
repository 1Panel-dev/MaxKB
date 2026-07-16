<template>
  <div class="conversation-plus">
    <div v-if="open && mode === 'drawer'" class="mask" @click="open = false" />

    <Sidebar
      :open="open"
      :mode="mode"
      :conversations="conversations"
      :current-id="currentChatId"
      @update:open="open = $event"
      @update:mode="mode = $event"
      @switch="handleSwitch"
      @delete="handleDelete"
      @rename="handleRename"
      @new="handleNewChat"
    />

    <ChatPanel
      ref="panelRef"
      :messages="messages"
      :loading="msgLoading"
      :stream-loading="streamLoading"
      :title="currentConversation?.name"
      :icon="appInfo?.icon"
      @send="handleSend"
      @stop="stopStream"
      @toggle="open = !open"
      @scroll="handleScroll"
    >
      <template #header>
        <slot name="header" />
      </template>
    </ChatPanel>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick, provide } from 'vue'
import Sidebar from './sidebar/index.vue'
import ChatPanel from './chat-panel/index.vue'
import { useChat } from './composable'

type OpenMode = boolean | 'auto'
type LayoutMode = 'push' | 'drawer' | 'auto'

const props = withDefaults(
  defineProps<{
    type?: 'CHAT' | 'DEBUG'
    applicationId?: string
    applicationDetails?: any
    defaultOpen?: OpenMode
    defaultMode?: LayoutMode
  }>(),
  {
    type: 'CHAT',
    defaultOpen: 'auto',
    defaultMode: 'auto'
  }
)

const emit = defineEmits<{
  openChat: [chatId: string]
  refresh: [chatId: string]
  close: []
}>()

const BREAKPOINT = 768
const isMobile = ref(window.innerWidth < BREAKPOINT)

// 计算初始 open 状态
const getInitialOpen = (): boolean => {
  if (props.defaultOpen === 'auto') {
    return !isMobile.value
  }
  return props.defaultOpen as boolean
}

// 计算初始 mode 状态
const getInitialMode = (): 'push' | 'drawer' => {
  if (props.defaultMode === 'auto') {
    return isMobile.value ? 'drawer' : 'push'
  }
  return props.defaultMode as 'push' | 'drawer'
}

const open = ref(getInitialOpen())
const mode = ref<'push' | 'drawer'>(getInitialMode())

const updateMobile = () => {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < BREAKPOINT
  
  // 只有 auto 模式才自动切换
  if (props.defaultOpen === 'auto') {
    // 移动端 -> 桌面端：展开
    if (wasMobile && !isMobile.value) {
      open.value = true
    }
    // 桌面端 -> 移动端：收起
    if (!wasMobile && isMobile.value) {
      open.value = false
    }
  }
  
  if (props.defaultMode === 'auto') {
    mode.value = isMobile.value ? 'drawer' : 'push'
  }
}

onMounted(() => window.addEventListener('resize', updateMobile))
onUnmounted(() => window.removeEventListener('resize', updateMobile))

const resolvedAppId = computed(() => props.applicationId || props.applicationDetails?.id)
const {
  appInfo,
  conversations,
  currentChatId,
  currentConversation,
  messages,
  msgLoading,
  streamLoading,
  loadConversations,
  openChat,
  switchChat,
  deleteChat,
  renameChat,
  sendMessage,
  stopStream
} = useChat(props.type, resolvedAppId)

const panelRef = ref()

provide('chat', {
  currentChatId,
  sendMessage,
  openChat,
  switchChat,
  deleteChat,
  renameChat,
  scrollToBottom: () => nextTick(() => panelRef.value?.scrollToBottom())
})

const handleNewChat = async () => {
  const chatId = await openChat()
  emit('openChat', chatId)
}

const handleSwitch = (id: string) => {
  switchChat(id)
}

const handleDelete = (id: string) => {
  deleteChat(id)
}

const handleRename = (id: string, name: string) => {
  renameChat(id, name)
}

const handleSend = async (text: string) => {
  if (!text.trim() || streamLoading.value) return

  if (!currentChatId.value) {
    await handleNewChat()
  }

  messages.value.push({
    role: 'USER',
    content: [{ type: 'TEXT', content: text }],
    id: ''
  })

  try {
    await sendMessage(text, {
      onScroll: () => nextTick(() => panelRef.value?.scrollToBottom())
    })
    emit('refresh', currentChatId.value)
  } catch {}
}

const handleScroll = () => {
  // Load more messages if needed
}

onMounted(() => {
  if (props.type === 'CHAT') {
    loadConversations()
  }
})
</script>

<style scoped>
.conversation-plus {
  --sb-w: 260px;
  --bg: #fff;
  --bg2: #fafafa;
  --bd: #dcdfe6;
  --t1: #303133;
  --t2: #606266;
  --t3: #909399;
  --hv: #f5f7fa;
  --ac: #ecf5ff;
  --ub: #d6e2ff;
  --ab: #f5f7fa;
  --mask: rgba(0, 0, 0, 0.4);
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  --danger-bg: rgba(239, 68, 68, 0.15);
  --danger-text: #ef4444;
  --focus-border: #3370ff;

  position: relative;
  display: flex;
  width: 100%;
  height: 100%;
  overflow: hidden;
  font-family: 'PingFang SC', 'Noto Sans SC', system-ui, sans-serif;
  background: var(--bg);
  color: var(--t1);
}

.mask {
  display: none;
  position: absolute;
  inset: 0;
  z-index: 30;
  background: var(--mask);
}

@media (max-width: 768px) {
  .mask {
    display: block;
  }
}
</style>
