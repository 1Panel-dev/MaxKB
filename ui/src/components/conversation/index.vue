<template>
  <div class="conversation-plus" :class="{ 'sidebar-open': sidebarOpen }">
    <div class="conv-sidebar" :class="{ open: sidebarOpen }">
      <Sidebar
        :conversations="store.conversations.value"
        :current-id="currentChatId"
        :mode="sidebarMode"
        :open="sidebarOpen"
        @open="handleOpen"
        @create="handleNewChat"
        @delete="handleDelete"
        @rename="handleRename"
      />
    </div>

    <div v-if="sidebarOpen && isMobile" class="conv-mask" @click="sidebarOpen = false" />

    <div class="conv-main">
      <ChatPanel
        ref="panelRef"
        :store="store"
        :current-chat-id="currentChatId"
        :app-info="store.appInfo.value"
        @toggle="sidebarOpen = !sidebarOpen"
        @send="handleSend"
        @stop="store.cancelStream(currentChatId)"
        @chat-opened="(id: string) => { currentChatId = id }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStoreByType } from './common/use-chat-store'
import type { ChatType } from './common/types'
import ChatPanel from './chat-panel/index.vue'
import Sidebar from './sidebar/index.vue'

type OpenMode = boolean | 'auto'
type LayoutMode = 'push' | 'drawer' | 'auto'

const props = withDefaults(
  defineProps<{
    type?: ChatType
    defaultOpen?: OpenMode
    defaultMode?: LayoutMode
  }>(),
  {
    type: 'CHAT',
    defaultOpen: 'auto',
    defaultMode: 'auto',
  },
)

const emit = defineEmits<{
  openChat: [chatId: string]
  refresh: [chatId: string]
}>()

const route = useRoute()
const applicationId = computed(() => route.params.id as string || route.params.applicationId as string || '')

const store = useChatStoreByType(props.type, applicationId.value)
provide('chat', store)

const BREAKPOINT = 768
const isMobile = ref(window.innerWidth < BREAKPOINT)
const updateMobile = () => { isMobile.value = window.innerWidth < BREAKPOINT }
onMounted(() => window.addEventListener('resize', updateMobile))
onBeforeUnmount(() => window.removeEventListener('resize', updateMobile))

const sidebarMode = ref<'push' | 'drawer'>(
  props.defaultMode === 'auto'
    ? isMobile.value ? 'drawer' : 'push'
    : props.defaultMode
)

const sidebarOpen = ref(
  props.defaultOpen === 'auto' ? !isMobile.value : props.defaultOpen
)

const panelRef = ref()
const currentChatId = ref('')

if (props.defaultOpen === 'auto') {
  watch(isMobile, (mobile) => {
    sidebarOpen.value = !mobile
  })
}

if (props.defaultMode === 'auto') {
  watch(isMobile, (mobile) => {
    sidebarMode.value = mobile ? 'drawer' : 'push'
  })
}

const handleNewChat = async () => {
  const id = await store.openChat(applicationId.value)
  currentChatId.value = id
  sidebarOpen.value = false
  emit('openChat', id)
}

const handleOpen = async (id: string) => {
  currentChatId.value = id
  await store.loadMessages(id)
  sidebarOpen.value = false
}

const handleDelete = async (id: string) => {
  await store.deleteChat(id)
  if (currentChatId.value === id) {
    currentChatId.value = store.conversations.value[0]?.id || ''
  }
}

const handleRename = (id: string, name: string) => {
  store.renameChat(id, name)
}

const handleSend = async (text: string, files?: any[]) => {
  if (!currentChatId.value) {
    await handleNewChat()
  }

  const cid = currentChatId.value

  store.pushMessage({
    role: 'USER',
    content: [{ type: 'QUESTION', content: text }],
    id: '',
  })

  store.pushMessage(store.createAnswerMessage())
  const aiMsg = store.messages.value[store.messages.value.length - 1]

  const payload: any = { message: text, stream: true, re_chat: false }
  if (files?.length) {
    payload.image_list = files.filter((f: any) => /\.(jpg|jpeg|png|gif|bmp)$/i.test(f.name))
    payload.document_list = files.filter((f: any) => /\.(pdf|docx|txt|xls|xlsx|md|html|csv)$/i.test(f.name))
    payload.audio_list = files.filter((f: any) => /\.(mp3|wav|ogg|aac|m4a)$/i.test(f.name))
    payload.video_list = files.filter((f: any) => /\.(mp4|avi|mkv|mov|flv|wmv)$/i.test(f.name))
  }

  store.startStream({
    cid,
    request: () => store.chat(cid, payload),
    onStream: (chunk: any) => store.appendChunk(aiMsg, chunk),
    onFinish: () => {
      aiMsg.write_ed = true
      emit('refresh', cid)
    },
    onFailure: () => {
      aiMsg.write_ed = true
    },
  })
}

const onResize = () => { isMobile.value = window.innerWidth < 768 }

onMounted(() => {
  window.addEventListener('resize', onResize)
  store.loadConversations()
  store.fetchAppInfo(applicationId.value)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  store.cancelStream(currentChatId.value)
})
</script>

<style scoped>
.conversation-plus {
  display: flex;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.conv-sidebar {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid var(--bd, #dcdfe6);
  overflow-y: auto;
  transition: width 0.25s ease, transform 0.25s ease;
}

.conv-sidebar:not(.open) {
  width: 0;
  overflow: hidden;
  border-right: none;
}

.conv-mask {
  display: none;
  position: absolute;
  inset: 0;
  z-index: 30;
  background: rgba(0, 0, 0, 0.4);
}

.conv-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

@media only screen and (max-width: 768px) {
  .conv-sidebar {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
  }

  .conv-sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 16px rgba(0, 0, 0, 0.2);
  }

  .conversation-plus.sidebar-open .conv-mask {
    display: block;
  }
}
</style>
