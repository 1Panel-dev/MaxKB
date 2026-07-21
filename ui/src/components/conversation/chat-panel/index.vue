<template>
  <main class="chat-panel" @drop.prevent="handleDrop" @dragover.prevent>
    <header v-if="showHeader" class="panel-header">
      <button class="header-btn" @click="$emit('toggle')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
      </button>
      <div class="header-info">
        <img v-if="appInfo?.icon" :src="appInfo.icon" class="header-icon" />
        <div class="header-text">
          <span v-if="appInfo?.name" class="header-app-name">{{ appInfo.name }}</span>
          <span class="header-title">{{ currentConversation?.name || '新对话' }}</span>
        </div>
      </div>
      <slot name="header" />
    </header>

    <div ref="msgBoxRef" class="panel-messages" @scroll="onScroll">
      <div v-if="messages.length === 0 && !msgLoading" class="welcome">
        <p class="welcome-title">{{ appInfo?.name || 'AI 助手' }}</p>
        <p class="welcome-sub">有什么可以帮你的？</p>
      </div>

      <template v-else>
        <div
          v-for="(msg, i) in messages"
          :key="msg.id || i"
          :class="['msg-row', msg.role === 'USER' ? 'user' : 'assistant']"
        >
          <ContentList :content-list="msg.content" />
        </div>

        <div v-if="streamLoading" class="msg-row assistant">
          <Loading :size="18" />
        </div>
      </template>
    </div>

    <footer class="panel-input">
      <div v-if="fileList.length" class="file-thumbs">
        <div v-for="(f, i) in fileList" :key="f.uid" class="file-thumb">
          <img v-if="f.previewUrl" :src="f.previewUrl" class="thumb-img" />
          <span v-else class="thumb-icon">📎</span>
          <span class="thumb-name">{{ f.name }}</span>
          <button class="thumb-rm" @click="removeFile(i)">✕</button>
        </div>
      </div>

      <div class="input-wrapper" :class="{ focused }">
        <input
          ref="fileInputRef"
          type="file"
          multiple
          :accept="acceptList"
          style="display: none"
          @change="handleFileSelect"
        />
        <textarea
          ref="inputRef"
          v-model="question.content"
          :disabled="streamLoading"
          :placeholder="placeholder"
          @keydown="onKeydown"
          @paste="handlePaste"
          @focus="focused = true"
          @blur="focused = false"
          rows="1"
        />
        <button
          class="upload-btn"
          :disabled="streamLoading"
          @click="fileInputRef?.click()"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M14 10v2.5a1.5 1.5 0 01-1.5 1.5h-9A1.5 1.5 0 012 12.5V10M8 2v8.5M5 5l3-3 3 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button
          v-if="!streamLoading"
          class="send-btn"
          :class="{ active: canSend }"
          :disabled="!canSend"
          @click="send"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 14V2M3 7l5-5 5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button v-else class="send-btn stop" @click="$emit('stop')">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="2" y="2" width="10" height="10" rx="2" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, reactive } from 'vue'
import ContentList from '../content-list/index.vue'
import Loading from '../loading/index.vue'
import { Scroll } from '../index'
import type { ChatMessage } from '../common/types'

const props = withDefaults(
  defineProps<{
    store: any
    currentChatId?: string
    appInfo?: { name: string; icon: string } | null
    showHeader?: boolean
  }>(),
  { showHeader: true },
)

const emit = defineEmits<{
  toggle: []
  send: [text: string, files?: any[]]
  stop: []
  chatOpened: [chatId: string]
}>()

const { messages, msgLoading, streamLoading, currentConversation } = props.store

const focused = ref(false)
const question = ref<any>({ content: '' })
const inputRef = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const msgBoxRef = ref<HTMLElement | null>(null)
let scroll: InstanceType<typeof Scroll> | null = null

// ── 文件 ────────────────────────────────────────────────
const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
const documentExts = ['pdf', 'docx', 'txt', 'xls', 'xlsx', 'md', 'html', 'csv']
const videoExts = ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv']
const audioExts = ['mp3', 'wav', 'ogg', 'aac', 'm4a']
const acceptList = [...imageExts, ...documentExts, ...videoExts, ...audioExts].map(e => `.${e}`).join(',')
const getExt = (name: string) => name.split('.').pop()?.toLowerCase() || ''
const isImage = (name: string) => imageExts.includes(getExt(name))

interface FileItem {
  uid: number; name: string; size: number; raw: File
  url?: string; file_id?: string; previewUrl?: string; uploading?: boolean
}

const fileList = ref<FileItem[]>([])
const uploadPromises = ref<Promise<any>[]>([])
const maxFiles = 10
const maxSizeMB = 50

const placeholder = computed(() => {
  if (streamLoading.value) return '正在回复中...'
  return '输入消息...'
})

const canSend = computed(() => question.value.content.trim() && !streamLoading.value)

const validateFile = (file: File): boolean => {
  if (fileList.value.length >= maxFiles) return false
  if (file.size === 0) return false
  if (file.size > maxSizeMB * 1024 * 1024) return false
  return true
}

const addFile = (file: File) => {
  if (!validateFile(file)) return
  const item: FileItem = reactive({
    uid: Date.now() + Math.random(),
    name: file.name,
    size: file.size,
    raw: file,
    uploading: true,
  })
  if (isImage(file.name)) item.previewUrl = URL.createObjectURL(file)
  fileList.value.push(item)

  const uploadPromise = (async () => {
    try {
      let cid = props.currentChatId
      if (!cid) {
        cid = await props.store.openChat()
        emit('chatOpened', cid)
      }
      const result = await props.store.uploadFile(file, cid)
      item.url = result.url
      const parts = result.url.split('/')
      item.file_id = parts[parts.length - 1]
    } catch (e) {
      console.error('upload failed:', e)
    } finally {
      item.uploading = false
    }
  })()

  uploadPromises.value.push(uploadPromise)
  uploadPromise.finally(() => {
    uploadPromises.value = uploadPromises.value.filter(p => p !== uploadPromise)
  })
}

const removeFile = (index: number) => {
  const item = fileList.value[index]
  if (item.previewUrl) URL.revokeObjectURL(item.previewUrl)
  fileList.value.splice(index, 1)
}

const clearFiles = () => {
  fileList.value.forEach(f => { if (f.previewUrl) URL.revokeObjectURL(f.previewUrl) })
  fileList.value = []
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  Array.from(input.files).forEach(addFile)
  input.value = ''
}

const handlePaste = (e: ClipboardEvent) => {
  const files = e.clipboardData?.files
  if (!files?.length) return
  e.preventDefault()
  Array.from(files).forEach(addFile)
}

const handleDrop = (e: DragEvent) => {
  const files = e.dataTransfer?.files
  if (!files) return
  Array.from(files).forEach(addFile)
}

const categorize = () => {
  const images: any[] = []; const documents: any[] = []
  const audio: any[] = []; const video: any[] = []; const files: any[] = []
  fileList.value.forEach(f => {
    const entry = { url: f.url || '', name: f.name }
    if (isImage(f.name)) images.push(entry)
    else if (documentExts.includes(getExt(f.name))) documents.push(entry)
    else if (audioExts.includes(getExt(f.name))) audio.push(entry)
    else if (videoExts.includes(getExt(f.name))) video.push(entry)
    else files.push(entry)
  })
  return { images, documents, audio, video, files }
}

// ── 发送 ────────────────────────────────────────────────
const send = async () => {
  if (!canSend.value) return
  if (uploadPromises.value.length) await Promise.all(uploadPromises.value)

  const text = question.value.content.trim()
  const media = categorize()

  let content = text
  if (!content) {
    const types = [
      media.images.length && '图片', media.documents.length && '文档',
      media.audio.length && '音频', media.video.length && '视频', media.files.length && '文件',
    ].filter(Boolean)
    content = types.length > 1 ? '文件消息' : `${types[0]}消息`
  }

  emit('send', content, fileList.value.length ? fileList.value : undefined)
  question.value.content = ''
  clearFiles()
}

// ── 键盘 ────────────────────────────────────────────────
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
}

// ── 滚动 ────────────────────────────────────────────────
const onScroll = () => {
  const el = msgBoxRef.value
  if (!el || el.scrollTop > 60) return
}

const scrollToBottom = () => { scroll?.forceBottom() }

onMounted(() => {
  if (msgBoxRef.value) scroll = new Scroll(msgBoxRef.value)
})

watch(() => messages.value.length, () => {
  nextTick(() => scroll?.scrollBottom())
})

defineExpose({ scrollToBottom })
</script>

<style scoped>
.chat-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
  background: var(--bg, #fff);
  overflow: hidden;
  position: relative;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 44px;
  padding: 0 12px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--bd, #dcdfe6);
}

.header-btn {
  width: 32px; height: 32px; border: none; background: transparent;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  border-radius: 6px; color: var(--t2, #606266); flex-shrink: 0;
}
.header-btn:hover { background: rgba(0, 0, 0, 0.05); }

.header-info {
  display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0;
}
.header-icon { width: 24px; height: 24px; border-radius: 6px; object-fit: cover; flex-shrink: 0; }
.header-text { display: flex; flex-direction: column; min-width: 0; }
.header-app-name { font-size: 11px; font-weight: 400; color: var(--t3, #909399); line-height: 1.2; }
.header-title { font-size: 13px; font-weight: 500; color: var(--t1, #303133); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.panel-messages {
  flex: 1; min-height: 0; overflow-y: auto; padding: 14px 12px;
  scrollbar-width: thin; display: flex; flex-direction: column; align-items: center;
}

.welcome {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  justify-content: center; text-align: center; padding: 32px 16px;
}
.welcome-title { font-size: 18px; font-weight: 600; color: var(--t1, #303133); margin-bottom: 8px; }
.welcome-sub { font-size: 14px; color: var(--t3, #909399); }

.msg-row {
  display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px;
  max-width: 680px; width: 100%; box-sizing: border-box;
}
.msg-row.user { align-items: flex-end; flex-direction: row-reverse; }
.msg-row.assistant { align-items: flex-start; }

.panel-input {
  flex-shrink: 0; padding: 12px 16px 16px; background: var(--bg, #fff);
  display: flex; flex-direction: column; align-items: center;
}

.file-thumbs {
  display: flex; gap: 8px; padding: 0 0 8px; flex-wrap: wrap; width: 100%; max-width: 680px;
}
.file-thumb {
  position: relative; display: flex; align-items: center; gap: 6px;
  padding: 4px 8px; border-radius: 6px; border: 1px solid var(--bd, #dcdfe6);
  font-size: 12px;
}
.thumb-img { width: 32px; height: 32px; border-radius: 4px; object-fit: cover; }
.thumb-name { max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--t2, #606266); }
.thumb-rm {
  position: absolute; top: -4px; right: -4px; width: 16px; height: 16px;
  border-radius: 50%; border: none; background: rgba(0, 0, 0, 0.5); color: #fff;
  font-size: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.15s;
}
.file-thumb:hover .thumb-rm { opacity: 1; }

.input-wrapper {
  width: 100%; max-width: 680px; display: flex; align-items: flex-end; gap: 8px;
  background: #fff; border: 1px solid var(--bd, #dcdfe6); border-radius: 16px;
  padding: 8px 8px 8px 16px; transition: border-color 0.2s, box-shadow 0.2s;
}
.input-wrapper.focused {
  border-color: var(--el-color-primary, #3370ff);
  box-shadow: 0 0 0 2px rgba(51, 112, 255, 0.1);
}

.input-wrapper textarea {
  flex: 1; border: none; outline: none; resize: none; font-family: inherit;
  font-size: 14px; line-height: 1.5; background: transparent;
  color: var(--t1, #303133); min-height: 24px; max-height: 160px;
  padding: 4px 0; word-break: break-word;
}
.input-wrapper textarea::placeholder { color: var(--t3, #909399); }

.upload-btn {
  width: 32px; height: 32px; border-radius: 8px; border: none;
  background: transparent; color: var(--t3, #909399); cursor: pointer;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
}
.upload-btn:hover { background: rgba(0, 0, 0, 0.05); color: var(--t2, #606266); }
.upload-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.send-btn {
  width: 36px; height: 36px; border-radius: 10px; border: none;
  background: var(--bd, #dcdfe6); color: var(--t3, #909399); cursor: not-allowed;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  transition: background 0.2s, color 0.2s, transform 0.1s;
}
.send-btn.active { background: var(--t1, #303133); color: #fff; cursor: pointer; }
.send-btn.active:hover { opacity: 0.85; }
.send-btn.active:active { transform: scale(0.92); }
.send-btn.stop { background: #ef4444; color: #fff; cursor: pointer; }
.send-btn.stop:hover { background: #dc2626; }
.send-btn.stop:active { transform: scale(0.92); }
</style>
