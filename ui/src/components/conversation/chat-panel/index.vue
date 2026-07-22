<template>
  <main class="chat-panel" @drop.prevent="handleDrop" @dragover.prevent>
    <header v-if="showHeader" class="panel-header">
      <button class="header-btn" @click="$emit('toggle')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M2 4h12M2 8h12M2 12h12"
            stroke="currentColor"
            stroke-width="1.6"
            stroke-linecap="round"
          />
        </svg>
      </button>
      <div class="header-info">
        <img v-if="appInfo?.icon" :src="appInfo.icon" class="header-icon" />
        <div class="header-text">
          <span v-if="appInfo?.name" class="header-app-name">{{ appInfo.name }}</span>
          <span class="header-title">{{ currentConversation?.abstract || '新对话' }}</span>
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
      <div class="operate-textarea">
        <!-- 文件预览区域 -->
        <div v-if="fileList.length" class="file-preview-list">
          <!-- 图片预览 -->
          <el-space wrap>
            <template v-for="(f, i) in imageFiles" :key="f.uid">
              <div
                class="file-item file-image"
                @mouseenter="showDelete = f.url || ''"
                @mouseleave="showDelete = ''"
              >
                <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
                  <el-icon style="font-size: 16px; top: 2px">
                    <CircleCloseFilled />
                  </el-icon>
                </div>
                <el-image
                  v-if="f.url"
                  :src="f.url"
                  fit="cover"
                  style="width: 40px; height: 40px; display: block"
                  class="border-r-6"
                />
                <el-image
                  v-else-if="f.previewUrl"
                  :src="f.previewUrl"
                  fit="cover"
                  style="width: 40px; height: 40px; display: block"
                  class="border-r-6"
                />
              </div>
            </template>
          </el-space>

          <!-- 文档预览 -->
          <el-row :gutter="10">
            <el-col
              v-for="(f, i) in documentFiles"
              :key="f.uid"
              :xs="24"
              :sm="12"
              :md="12"
              :lg="12"
              :xl="12"
              class="mb-8"
            >
              <el-card
                shadow="never"
                style="--el-card-padding: 8px; max-width: 100%"
                class="file-card"
              >
                <div
                  class="flex-between align-center"
                  @mouseenter="showDelete = f.url || ''"
                  @mouseleave="showDelete = ''"
                >
                  <div class="flex align-center">
                    <img :src="getFileIcon(f.name)" alt="" width="24" />
                    <div class="ml-4 ellipsis-1" :title="f.name">
                      {{ f.name }}
                    </div>
                  </div>
                  <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
                    <el-icon style="font-size: 16px; top: 2px">
                      <CircleCloseFilled />
                    </el-icon>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 音频预览 -->
          <el-row :gutter="10">
            <el-col
              v-for="(f, i) in audioFiles"
              :key="f.uid"
              :xs="24"
              :sm="12"
              :md="12"
              :lg="12"
              :xl="12"
              class="mb-8"
            >
              <el-card shadow="never" style="--el-card-padding: 8px" class="file-card">
                <div
                  class="flex-between align-center"
                  @mouseenter="showDelete = f.url || ''"
                  @mouseleave="showDelete = ''"
                >
                  <div class="flex align-center">
                    <img :src="getFileIcon(f.name)" alt="" width="24" />
                    <div class="ml-4 ellipsis-1" :title="f.name">
                      {{ f.name }}
                    </div>
                  </div>
                  <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
                    <el-icon style="font-size: 16px; top: 2px">
                      <CircleCloseFilled />
                    </el-icon>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 视频预览 -->
          <el-space wrap>
            <template v-for="(f, i) in videoFiles" :key="f.uid">
              <div
                class="file-item file-image"
                @mouseenter="showDelete = f.url || ''"
                @mouseleave="showDelete = ''"
              >
                <div v-if="showDelete === f.url" class="delete-icon" @click="removeFile(i)">
                  <el-icon style="font-size: 16px; top: 2px">
                    <CircleCloseFilled />
                  </el-icon>
                </div>
                <video
                  v-if="f.url"
                  :src="f.url"
                  controls
                  style="width: 100px; display: block"
                  class="border-r-6"
                  autoplay
                />
              </div>
            </template>
          </el-space>
        </div>

        <!-- 输入框 -->
        <el-input
          ref="inputRef"
          v-model="question.content"
          :autosize="{ minRows: 1, maxRows: 10 }"
          type="textarea"
          :placeholder="placeholder"
          :maxlength="100000"
          @keydown.enter="handleKeydown"
          @paste="handlePaste"
          class="chat-operate-textarea"
          clearable
        />

        <!-- 操作栏 -->
        <div class="operate flex-between">
          <div></div>
          <div class="flex align-center">
            <input
              ref="fileInputRef"
              type="file"
              multiple
              :accept="acceptList"
              style="display: none"
              @change="handleFileSelect"
            />
            <el-tooltip effect="dark" placement="top" popper-class="upload-tooltip-width">
              <template #content>
                <div class="break-all pre-wrap">
                  支持上传图片、文档、音频、视频文件，最多{{ maxFiles }}个，单个文件最大{{
                    maxSizeMB
                  }}MB
                </div>
              </template>
              <el-button
                text
                :disabled="streamLoading || fileList.length >= maxFiles"
                @click="fileInputRef?.click()"
              >
                <el-icon :size="20"><Paperclip /></el-icon>
              </el-button>
            </el-tooltip>
            <el-divider direction="vertical" />
            <el-button text class="sent-button" :disabled="!canSend" @click="send">
              <el-icon v-if="!streamLoading" :size="20">
                <Promotion />
              </el-icon>
              <el-icon v-else :size="20" @click.stop="$emit('stop')">
                <VideoPause />
              </el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, reactive } from 'vue'
import { CircleCloseFilled, Paperclip, Promotion, VideoPause } from '@element-plus/icons-vue'
import ContentList from '../content-list/index.vue'
import Loading from '../loading/index.vue'
import { Scroll } from '../index'
import { useChatStoreByType } from '../common/use-chat-store'
import type { ChatType } from '../common/types'

const props = withDefaults(
  defineProps<{
    type?: ChatType
    appInfo?: { name: string; icon: string } | null
    showHeader?: boolean
  }>(),
  { type: 'CHAT', showHeader: true },
)

const emit = defineEmits<{
  toggle: []
  refresh: [chatId: string]
  stop: []
}>()

const store = useChatStoreByType(props.type)
const { messages, msgLoading, streamLoading, currentConversation, currentChatId } = store

const question = ref<any>({ content: '' })
const inputRef = ref<any>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const msgBoxRef = ref<HTMLElement | null>(null)
let scroll: InstanceType<typeof Scroll> | null = null

// ── 文件 ────────────────────────────────────────────────
const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
const documentExts = ['pdf', 'docx', 'txt', 'xls', 'xlsx', 'md', 'html', 'csv']
const videoExts = ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv']
const audioExts = ['mp3', 'wav', 'ogg', 'aac', 'm4a']
const acceptList = [...imageExts, ...documentExts, ...videoExts, ...audioExts]
  .map((e) => `.${e}`)
  .join(',')
const getExt = (name: string) => name.split('.').pop()?.toLowerCase() || ''
const isImage = (name: string) => imageExts.includes(getExt(name))
const isDocument = (name: string) => documentExts.includes(getExt(name))
const isAudio = (name: string) => audioExts.includes(getExt(name))
const isVideo = (name: string) => videoExts.includes(getExt(name))

interface FileItem {
  uid: number
  name: string
  size: number
  raw: File
  url?: string
  file_id?: string
  previewUrl?: string
  uploading?: boolean
}

const fileList = ref<FileItem[]>([])
const uploadPromises = ref<Promise<any>[]>([])
const maxFiles = 10
const maxSizeMB = 50
const showDelete = ref('')

const placeholder = computed(() => {
  if (streamLoading.value) return '正在回复中...'
  return '输入消息...'
})

const canSend = computed(
  () => (question.value.content.trim() || fileList.value.length > 0) && !streamLoading.value,
)

// 分类文件列表
const imageFiles = computed(() => fileList.value.filter((f) => isImage(f.name)))
const documentFiles = computed(() => fileList.value.filter((f) => isDocument(f.name)))
const audioFiles = computed(() => fileList.value.filter((f) => isAudio(f.name)))
const videoFiles = computed(() => fileList.value.filter((f) => isVideo(f.name)))

const getFileIcon = (name: string) => {
  const ext = getExt(name)
  const iconMap: Record<string, string> = {
    pdf: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    doc: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    docx: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    xls: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    xlsx: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    txt: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    md: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    html: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    csv: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg',
    mp3: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/headset.svg',
    wav: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/headset.svg',
    ogg: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/headset.svg',
    aac: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/headset.svg',
    m4a: 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/headset.svg',
  }
  return (
    iconMap[ext] ||
    'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg'
  )
}

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
      let cid = currentChatId.value
      if (!cid) {
        cid = await store.openChat(store.applicationId.value)
        currentChatId.value = cid
      }
      const result = await store.uploadFile(file, cid)
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
    uploadPromises.value = uploadPromises.value.filter((p) => p !== uploadPromise)
  })
}

const removeFile = (index: number) => {
  const item = fileList.value[index]
  if (item.previewUrl) URL.revokeObjectURL(item.previewUrl)
  fileList.value.splice(index, 1)
}

const clearFiles = () => {
  fileList.value.forEach((f) => {
    if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
  })
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
  const images: any[] = []
  const documents: any[] = []
  const audio: any[] = []
  const video: any[] = []
  const files: any[] = []
  fileList.value.forEach((f) => {
    const entry = { url: f.url || '', file_id: f.file_id || '', name: f.name }
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

  // 如果没有当前对话，创建新对话
  if (!currentChatId.value) {
    const id = await store.openChat(store.applicationId.value)
    currentChatId.value = id
    await store.loadConversations()
  }

  const cid = currentChatId.value

  // 判断是否是第一条消息，如果是则更新对话的 abstract
  const isFirstMessage = messages.value.length === 0
  if (isFirstMessage && text) {
    const abstract = text.substring(0, 256)
    await store.renameChat(cid, abstract)
  }

  // 分类文件
  const images = fileList.value
    .filter((f) => isImage(f.name))
    .map((f) => ({ url: f.url, file_id: f.file_id, name: f.name }))
  const documents = fileList.value
    .filter((f) => isDocument(f.name))
    .map((f) => ({ url: f.url, file_id: f.file_id, name: f.name }))
  const audio = fileList.value
    .filter((f) => isAudio(f.name))
    .map((f) => ({ url: f.url, file_id: f.file_id, name: f.name }))
  const video = fileList.value
    .filter((f) => isVideo(f.name))
    .map((f) => ({ url: f.url, file_id: f.file_id, name: f.name }))
  const other = fileList.value
    .filter((f) => !isImage(f.name) && !isDocument(f.name) && !isAudio(f.name) && !isVideo(f.name))
    .map((f) => ({ url: f.url, file_id: f.file_id, name: f.name }))

  // 构建 question content
  const questionContent: any = { type: 'QUESTION', content: text }
  if (images.length) questionContent.image_list = images
  if (documents.length) questionContent.document_list = documents
  if (audio.length) questionContent.audio_list = audio
  if (video.length) questionContent.video_list = video
  if (other.length) questionContent.other_list = other

  store.pushMessage({
    role: 'USER',
    content: [questionContent],
    id: '',
  })

  store.pushMessage(store.createAnswerMessage())
  const aiMsg = messages.value[messages.value.length - 1]

  // 构建 API payload
  const message: any = { content: text, type: 'QUESTION' }
  if (images.length) message.image_list = images
  if (documents.length) message.document_list = documents
  if (audio.length) message.audio_list = audio
  if (video.length) message.video_list = video
  if (other.length) message.other_list = other

  const payload: any = { message, stream: true, re_chat: false }

  store.startStream({
    cid,
    request: () => store.chat(cid, payload),
    onStream: (chunk: any) => {
      store.appendChunk(aiMsg, chunk)
      scrollToBottom()
    },
    onFinish: () => {
      aiMsg.write_ed = true
      emit('refresh', cid)
    },
    onFailure: () => {
      aiMsg.write_ed = true
    },
  })

  question.value.content = ''
  clearFiles()
}

// ── 键盘 ────────────────────────────────────────────────
const handleKeydown = (e: KeyboardEvent) => {
  const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent,
  )
  // 如果是移动端，且按下回车键，不直接发送
  if (isMobile && e.key === 'Enter') {
    return
  }
  if (!e.ctrlKey && !e.shiftKey && !e.altKey && !e.metaKey) {
    e.preventDefault()
    if (canSend.value && !e.isComposing) {
      send()
    }
  } else {
    // 如果同时按下ctrl/shift/cmd/opt +enter，则会换行
    const textarea = inputRef.value?.$el?.querySelector(
      '.el-textarea__inner',
    ) as HTMLTextAreaElement
    if (textarea) {
      const startPos = textarea.selectionStart
      const endPos = textarea.selectionEnd
      e.preventDefault()
      question.value.content =
        question.value.content.slice(0, startPos) + '\n' + question.value.content.slice(endPos)
      nextTick(() => {
        textarea.setSelectionRange(startPos + 1, startPos + 1)
      })
    }
  }
}

// ── 滚动 ────────────────────────────────────────────────
const onScroll = () => {
  const el = msgBoxRef.value
  if (!el || el.scrollTop > 60) return
}

const scrollToBottom = () => {
  scroll?.forceBottom()
}

onMounted(() => {
  if (msgBoxRef.value) scroll = new Scroll(msgBoxRef.value)
})

watch(
  () => messages.value.length,
  () => {
    nextTick(() => scroll?.scrollBottom())
  },
)

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
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: var(--t2, #606266);
  flex-shrink: 0;
}
.header-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.header-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}
.header-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.header-app-name {
  font-size: 11px;
  font-weight: 400;
  color: var(--t3, #909399);
  line-height: 1.2;
}
.header-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--t1, #303133);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.panel-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px 12px;
  scrollbar-width: thin;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px 16px;
}
.welcome-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--t1, #303133);
  margin-bottom: 8px;
}
.welcome-sub {
  font-size: 14px;
  color: var(--t3, #909399);
}

.msg-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
  max-width: 680px;
  width: 100%;
  box-sizing: border-box;
}
.msg-row.user {
  align-items: flex-end;
  flex-direction: row-reverse;
}
.msg-row.assistant {
  align-items: flex-start;
}

.panel-input {
  flex-shrink: 0;
  padding: 12px 16px 16px;
  background: var(--bg, #fff);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.operate-textarea {
  width: 100%;
  max-width: 680px;
  box-shadow: 0px 6px 24px 0px rgba(var(--el-text-color-primary-rgb), 0.08);
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #ffffff;
  box-sizing: border-box;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.operate-textarea:focus-within {
  border: 1px solid var(--el-color-primary);
}

.operate-textarea :deep(.el-textarea__inner) {
  border-radius: 8px !important;
  box-shadow: none;
  resize: none;
  padding: 13px 16px;
  box-sizing: border-box;
  min-height: 47px !important;
}

.file-preview-list {
  padding: 8px 12px;
}

.file-item {
  position: relative;
  overflow: inherit;
}

.file-image .delete-icon {
  position: absolute;
  right: -5px;
  top: -5px;
  z-index: 1;
}

.delete-icon {
  cursor: pointer;
  color: var(--el-color-info);
}

.delete-icon:hover {
  color: var(--el-color-danger);
}

.file-card {
  cursor: pointer;
}

.operate {
  padding: 6px 10px;
}

.sent-button {
  max-height: none;
}

.sent-button .el-icon {
  font-size: 24px;
}

.mb-8 {
  margin-bottom: 8px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
}

.align-center {
  align-items: center;
}

.flex {
  display: flex;
}

.ellipsis-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.border-r-6 {
  border-radius: 6px;
}

.break-all {
  word-break: break-all;
}

.pre-wrap {
  white-space: pre-wrap;
}

.ml-4 {
  margin-left: 4px;
}

@media only screen and (max-width: 768px) {
  .panel-input {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 10;
  }
}

.upload-tooltip-width {
  width: 300px;
}
</style>
