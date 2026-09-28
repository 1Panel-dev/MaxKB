import { ref, computed, reactive, watch, inject, type Ref, type InjectionKey } from 'vue'
import { IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS } from '@/constants/file-type'
import { isImage, isDocument, isAudio, isVideo } from '@/utils/icon'
import type { ChatMessage, Conversation, SendMessageOptions } from '../../core/types'

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

type MessageAttachmentKey = 'image_list' | 'document_list' | 'audio_list' | 'video_list' | 'other_list'
type MessageAttachment = Pick<FileItem, 'url' | 'file_id' | 'name'>
type QuestionMessage = {
  type: 'QUESTION'
  content: string
} & Partial<Record<MessageAttachmentKey, MessageAttachment[]>>

// 仅注入消息输入所需的会话、上传和发送能力。
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
  const { conversations, getChatId, renameChat, composerResetSignal, messages, loading, sendMessage, uploadFile, stop } = deps

  // 输入状态与附件限制
  const question = ref('')
  const fileList = ref<FileItem[]>([])
  const sending = ref(false)
  const maxFiles = 10
  const maxSizeMB = 50

  // TODO 格式 不行
  const acceptList = [...IMAGE_EXTENSIONS, ...DOCUMENT_EXTENSIONS, ...VIDEO_EXTENSIONS, ...AUDIO_EXTENSIONS].map((e) => `.${e}`).join(',')

  const placeholder = computed(() => (loading.value ? '正在回复中...' : '输入消息...'))
  const canSend = computed(() => (question.value.trim().length > 0 || fileList.value.length > 0) && !loading.value && !sending.value)

  const imageFiles = computed(() => fileList.value.filter((attachment) => isImage(attachment.name)))

  // 附件上传与本地预览
  const uploadPromises = ref<Promise<void>[]>([])

  const validateFile = (file: File) => fileList.value.length < maxFiles && file.size > 0 && file.size <= maxSizeMB * 1024 * 1024

  const addFile = (file: File) => {
    if (!validateFile(file)) return
    const attachment: FileItem = reactive({
      uid: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      raw: file,
      uploading: true,
    })
    if (isImage(file.name) || isAudio(file.name) || isVideo(file.name)) {
      attachment.previewUrl = URL.createObjectURL(file)
    }
    fileList.value.push(attachment)

    const uploadPromise = (async () => {
      try {
        const chatId = getChatId()
        const url = await uploadFile(file, chatId)
        attachment.url = url
        attachment.file_id = url.split('/').pop()
      } catch (e) {
        console.error('upload failed:', e)
      } finally {
        attachment.uploading = false
      }
    })()
    uploadPromises.value.push(uploadPromise)
    uploadPromise.finally(() => {
      uploadPromises.value = uploadPromises.value.filter((pendingUpload) => pendingUpload !== uploadPromise)
    })
  }

  const addFiles = (files: FileList | File[] | null | undefined) => {
    if (!files) return
    Array.from(files).forEach(addFile)
  }

  const removeFile = (index: number) => {
    const attachment = fileList.value[index]
    if (!attachment) return
    if (attachment.previewUrl) URL.revokeObjectURL(attachment.previewUrl)
    fileList.value.splice(index, 1)
  }

  const clearFiles = () => {
    fileList.value.forEach((attachment) => {
      if (attachment.previewUrl) URL.revokeObjectURL(attachment.previewUrl)
    })
    fileList.value = []
  }

  // 等待附件上传后发送，首条消息同步会话标题。
  const send = async () => {
    if (!canSend.value) return
    sending.value = true
    try {
      if (uploadPromises.value.length) await Promise.all(uploadPromises.value)

      const questionText = question.value.trim()
      const chatId = getChatId()

      // 首条消息先显示会话标题，流结束后再保存标题。
      const isFirstMessage = messages.value.length === 0
      const abstract = questionText.substring(0, 256)
      if (isFirstMessage && !conversations.value.some((conversation) => conversation.id === chatId)) {
        // 本地新会话尚未由历史接口返回，使用首次发送时间展示相对时间。
        const createTime = new Date().toISOString()
        conversations.value.unshift({
          id: chatId,
          abstract: questionText ? abstract : '新对话',
          create_time: createTime,
          update_time: createTime,
        })
      }

      // 一次遍历完成附件分类，仅提交有附件的字段。
      const message: QuestionMessage = { type: 'QUESTION', content: questionText }
      for (const attachment of fileList.value) {
        let attachmentKey: MessageAttachmentKey = 'other_list'
        if (isImage(attachment.name)) attachmentKey = 'image_list'
        else if (isDocument(attachment.name)) attachmentKey = 'document_list'
        else if (isAudio(attachment.name)) attachmentKey = 'audio_list'
        else if (isVideo(attachment.name)) attachmentKey = 'video_list'

        const attachments = (message[attachmentKey] ??= [])
        attachments.push({ url: attachment.url, file_id: attachment.file_id, name: attachment.name })
      }

      sendMessage({
        chatId,
        message,
        newQuestion: true,
        questionContent: { ...message },
        reChat: false,
        onComplete: (e) => {
          if (!e && isFirstMessage && questionText) renameChat(chatId, abstract).catch(() => {})
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
    maxFiles,
    maxSizeMB,
    acceptList,
    loading,
    placeholder,
    canSend,
    imageFiles,
    addFile,
    addFiles,
    removeFile,
    send,
    stop,
  }
}

export type MessageInputStore = ReturnType<typeof createMessageInputStore>

export const MESSAGE_INPUT_KEY: InjectionKey<MessageInputStore> = Symbol('message-input')

export function useMessageInputStore(): MessageInputStore {
  const store = inject(MESSAGE_INPUT_KEY)
  if (!store) throw new Error('useMessageInputStore 必须在 ConversationView 内使用')
  return store
}
