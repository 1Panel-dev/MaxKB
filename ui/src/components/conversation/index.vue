<template>
  <div class="conversation-plus" :class="{ 'sidebar-open': sidebarOpen }">
    <div class="conv-sidebar" :class="{ open: sidebarOpen }">
      <Sidebar
        :type="type"
        :mode="sidebarMode"
        :open="sidebarOpen"
        @update:open="sidebarOpen = $event"
        @update:mode="sidebarMode = $event"
      />
    </div>

    <div v-if="sidebarOpen && isMobile" class="conv-mask" @click="sidebarOpen = false" />

    <div class="conv-main">
      <ChatPanel
        ref="panelRef"
        :type="type"
        :app-info="store.appInfo.value"
        @toggle="sidebarOpen = !sidebarOpen"
        @send="handleSend"
        @stop="store.cancelStream(store.currentChatId.value)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, provide } from 'vue'
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

const store = useChatStoreByType(props.type)
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

const handleSend = async (text: string, files?: any[]) => {
  if (!store.currentChatId.value) {
    const id = await store.openChat(store.applicationId.value)
    store.currentChatId.value = id
    await store.loadConversations()
  }

  const cid = store.currentChatId.value

  // 判断是否是第一条消息，如果是则更新对话的 abstract
  const isFirstMessage = store.messages.value.length === 0
  if (isFirstMessage && text.trim()) {
    const abstract = text.trim().substring(0, 256)
    await store.renameChat(cid, abstract)
  }

  // 分类文件
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
  const docExts = ['pdf', 'docx', 'txt', 'xls', 'xlsx', 'md', 'html', 'csv']
  const audioExts = ['mp3', 'wav', 'ogg', 'aac', 'm4a']
  const videoExts = ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv']
  const getExt = (name: string) => name.split('.').pop()?.toLowerCase() || ''
  const byExt = (exts: string[]) => (f: any) => exts.includes(getExt(f.name))

  const images = files?.filter(byExt(imageExts)).map((f: any) => ({ url: f.url, file_id: f.file_id, name: f.name })) || []
  const documents = files?.filter(byExt(docExts)).map((f: any) => ({ url: f.url, file_id: f.file_id, name: f.name })) || []
  const audio = files?.filter(byExt(audioExts)).map((f: any) => ({ url: f.url, file_id: f.file_id, name: f.name })) || []
  const video = files?.filter(byExt(videoExts)).map((f: any) => ({ url: f.url, file_id: f.file_id, name: f.name })) || []
  const other = files?.filter((f: any) => ![...imageExts, ...docExts, ...audioExts, ...videoExts].includes(getExt(f.name)))
    .map((f: any) => ({ url: f.url, file_id: f.file_id, name: f.name })) || []

  // 构建 question content
  const questionContent: any = { type: 'QUESTION', content: text }
  if (images.length) questionContent.images = images
  if (documents.length) questionContent.documents = documents
  if (audio.length) questionContent.audio = audio
  if (video.length) questionContent.video = video
  if (other.length) questionContent.files = other

  store.pushMessage({
    role: 'USER',
    content: [questionContent],
    id: '',
  })

  store.pushMessage(store.createAnswerMessage())
  const aiMsg = store.messages.value[store.messages.value.length - 1]

  // 构建 API payload
  const payload: any = { message: text, stream: true, re_chat: false }
  if (images.length) payload.image_list = images
  if (documents.length) payload.document_list = documents
  if (audio.length) payload.audio_list = audio
  if (video.length) payload.video_list = video
  if (other.length) payload.other_list = other

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
  store.fetchAppInfo(store.applicationId.value)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  store.cancelStream(store.currentChatId.value)
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
