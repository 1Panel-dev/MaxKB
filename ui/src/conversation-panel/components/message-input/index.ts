import { ref, computed, reactive, watch, inject, type Ref, type InjectionKey } from 'vue'
import type { ChatMessage, Conversation, SendMessageOptions } from '../../core/types'

const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
const documentExts = ['pdf', 'docx', 'txt', 'xls', 'xlsx', 'md', 'html', 'csv']
const videoExts = ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv']
const audioExts = ['mp3', 'wav', 'ogg', 'aac', 'm4a']
const getExt = (name: string) => name.split('.').pop()?.toLowerCase() || ''
const isImage = (name: string) => imageExts.includes(getExt(name))
const isDocument = (name: string) => documentExts.includes(getExt(name))
const isAudio = (name: string) => audioExts.includes(getExt(name))
const isVideo = (name: string) => videoExts.includes(getExt(name))

export interface FileItem {
  uid: number
  name: string
  size: number
  raw: File
  url?: string
  file_id?: string
  previewUrl?: string
  uploading?: boolean
}

// 只声明本组件真正用到的依赖(接口隔离),不接收整个别人的 store
export interface MessageInputDeps {
  // 来自 conversation-list
  conversations: Ref<Conversation[]>
  getChatId: () => string
  renameChat: (id: string, name: string) => Promise<void>
  composerResetSignal: Ref<number>
  // 来自 message-list
  messages: Ref<ChatMessage[]>
  loading: Ref<boolean>
  sendMessage: (opts: SendMessageOptions) => void
  uploadFile: (file: File, chatId: string) => Promise<string>
  stop: () => void
}

/**
 * message-input 组件 store:本组件独有——输入内容 + 暂存文件 + 发送。
 */
export function createMessageInputStore(deps: MessageInputDeps) {
  const { conversations, getChatId, renameChat, composerResetSignal, messages, loading, sendMessage, uploadFile, stop } =
    deps

  const question = ref('')
  const fileList = ref<FileItem[]>([])
  const uploadPromises = ref<Promise<any>[]>([])
  const showDelete = ref('')
  const sending = ref(false)
  const maxFiles = 10
  const maxSizeMB = 50
  const acceptList = [...imageExts, ...documentExts, ...videoExts, ...audioExts].map((e) => `.${e}`).join(',')

  const placeholder = computed(() => (loading.value ? '正在回复中...' : '输入消息...'))
  const canSend = computed(
    () => (question.value.trim() || fileList.value.length > 0) && !loading.value && !sending.value,
  )

  const imageFiles = computed(() => fileList.value.filter((f) => isImage(f.name)))
  const documentFiles = computed(() => fileList.value.filter((f) => isDocument(f.name)))
  const audioFiles = computed(() => fileList.value.filter((f) => isAudio(f.name)))
  const videoFiles = computed(() => fileList.value.filter((f) => isVideo(f.name)))

  const getFileIcon = (name: string) => {
    const ext = getExt(name)
    const doc = 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/document.svg'
    const audio = 'https://cdn.jsdelivr.net/npm/@element-plus/icons-vue@2.3.1/dist/svg/headset.svg'
    const iconMap: Record<string, string> = {
      pdf: doc, doc, docx: doc, xls: doc, xlsx: doc, txt: doc, md: doc, html: doc, csv: doc,
      mp3: audio, wav: audio, ogg: audio, aac: audio, m4a: audio,
    }
    return iconMap[ext] || doc
  }

  const validateFile = (file: File) =>
    fileList.value.length < maxFiles && file.size > 0 && file.size <= maxSizeMB * 1024 * 1024

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
        const cid = getChatId()
        const url = await uploadFile(file, cid)
        item.url = url
        const parts = url.split('/')
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

  const addFiles = (files: FileList | File[] | null | undefined) => {
    if (!files) return
    Array.from(files).forEach(addFile)
  }

  const removeFile = (index: number) => {
    const item = fileList.value[index]
    if (!item) return
    if (item.previewUrl) URL.revokeObjectURL(item.previewUrl)
    fileList.value.splice(index, 1)
  }

  const clearFiles = () => {
    fileList.value.forEach((f) => {
      if (f.previewUrl) URL.revokeObjectURL(f.previewUrl)
    })
    fileList.value = []
  }

  const send = async () => {
    if (sending.value || !canSend.value) return
    sending.value = true
    try {
      if (uploadPromises.value.length) await Promise.all(uploadPromises.value)

      const text = question.value.trim()
      const cid = getChatId()

      // 首条消息:此刻把会话 push 进左侧列表(标题乐观更新),流结束后 renameChat 落库
      const isFirstMessage = messages.value.length === 0
      const abstract = text.substring(0, 256)
      if (isFirstMessage && !conversations.value.some((c: any) => c.id === cid)) {
        conversations.value.unshift({ id: cid, abstract: text ? abstract : '新对话' })
      }

      const pick = (pred: (n: string) => boolean) =>
        fileList.value.filter((f) => pred(f.name)).map((f) => ({ url: f.url, file_id: f.file_id, name: f.name }))
      const images = pick(isImage)
      const documents = pick(isDocument)
      const audio = pick(isAudio)
      const video = pick(isVideo)
      const other = fileList.value
        .filter((f) => !isImage(f.name) && !isDocument(f.name) && !isAudio(f.name) && !isVideo(f.name))
        .map((f) => ({ url: f.url, file_id: f.file_id, name: f.name }))

      const questionContent: any = { type: 'QUESTION', content: text }
      const message: any = { content: text, type: 'QUESTION' }
      if (images.length) questionContent.image_list = message.image_list = images
      if (documents.length) questionContent.document_list = message.document_list = documents
      if (audio.length) questionContent.audio_list = message.audio_list = audio
      if (video.length) questionContent.video_list = message.video_list = video
      if (other.length) questionContent.other_list = message.other_list = other

      sendMessage({
        chatId: cid,
        message,
        newQuestion: true,
        questionContent,
        reChat: false,
        onComplete: (e) => {
          if (!e && isFirstMessage && text) renameChat(cid, abstract).catch(() => {})
        },
      })
      question.value = ''
      clearFiles()
    } catch (e) {
      console.error('send failed:', e)
      loading.value = false
    } finally {
      sending.value = false
    }
  }

  // 新建/切换会话时清空暂存文件与输入
  watch(
    () => composerResetSignal.value,
    () => {
      clearFiles()
      question.value = ''
    },
  )

  return {
    question,
    fileList,
    showDelete,
    maxFiles,
    maxSizeMB,
    acceptList,
    loading: loading,
    placeholder,
    canSend,
    imageFiles,
    documentFiles,
    audioFiles,
    videoFiles,
    getFileIcon,
    addFile,
    addFiles,
    removeFile,
    send,
    stop: stop,
  }
}

export type MessageInputStore = ReturnType<typeof createMessageInputStore>

export const MESSAGE_INPUT_KEY: InjectionKey<MessageInputStore> = Symbol('message-input')

export function useMessageInputStore(): MessageInputStore {
  const store = inject(MESSAGE_INPUT_KEY)
  if (!store) throw new Error('useMessageInputStore 必须在 ConversationView 内使用')
  return store
}
