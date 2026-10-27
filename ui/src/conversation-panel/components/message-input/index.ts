import { ref, computed, reactive, watch, inject, type Ref, type InjectionKey } from 'vue'
import { IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS } from '@/constants/file-type'
import { isImage, isDocument, isAudio, isVideo } from '@/utils/icon'
import type { Dict } from '@/api/types'
import type { ChatMessage, Conversation, ConversationAppInfo, SendMessageOptions } from '../../core/types'

export interface FileItem {
  uid: number
  name: string
  size: number
  raw: File
  url?: string
  file_id?: string
  previewUrl?: string
  status: 'ready' | 'uploading' | 'success' | 'fail'
  errMsg?: string
  /** 上传进度 0-100 */
  progress?: number
}

type MessageAttachmentKey = 'image_list' | 'document_list' | 'audio_list' | 'video_list' | 'other_list'
type MessageAttachment = Pick<FileItem, 'url' | 'file_id' | 'name'>
type QuestionAttachments = Partial<Record<MessageAttachmentKey, MessageAttachment[]>>
type QuestionMessage = {
  type: 'QUESTION'
  content: string
} & QuestionAttachments

/** 非输入框发起的提问可附带的附件与表单数据（对应 v2 的 other_params_data）。 */
export interface QuestionOptions {
  attachments?: QuestionAttachments
  formData?: Dict<unknown>
}

// 仅注入消息输入所需的会话、上传和发送能力。
export interface MessageInputDeps {
  // 来自 conversation-list
  conversations: Ref<Conversation[]>
  getChatId: () => string
  renameChat: (id: string, name: string) => Promise<void>
  composerResetSignal: Ref<number>
  // 来自 message-list
  messages: Ref<ChatMessage[]>
  /** 对话加载(回答生成中):只读,由 message-list 维护 */
  streamLoading: Readonly<Ref<boolean>>
  sendMessage: (opts: SendMessageOptions) => void
  uploadFile: (file: File, chatId: string, onProgress?: (percent: number) => void) => Promise<string>
  stop: () => void
  /** 当前智能体信息：只读，由 view 加载维护。 */
  appInfo: Readonly<Ref<ConversationAppInfo | null>>
  /** 禁用输入与发送，如门户没有可用智能体时；不传时始终可用。 */
  disabled?: Readonly<Ref<boolean>>
}

// 上传请求返回前进度条的最大值
const UPLOAD_PROGRESS_PENDING_MAX = 95

/**
 * message-input 组件 store:本组件独有——输入内容 + 暂存文件 + 发送。
 */
export function createMessageInputStore(deps: MessageInputDeps) {
  const { conversations, getChatId, renameChat, composerResetSignal, messages, streamLoading, sendMessage, uploadFile, stop, appInfo } = deps
  const disabled = computed(() => deps.disabled?.value ?? false)

  // 输入状态与附件限制
  const question = ref('')
  const fileList = ref<FileItem[]>([])
  const sending = ref(false)
  const maxFiles = 10
  const maxSizeMB = 50

  // TODO 格式 不行
  const acceptList = [...IMAGE_EXTENSIONS, ...DOCUMENT_EXTENSIONS, ...VIDEO_EXTENSIONS, ...AUDIO_EXTENSIONS].map((e) => `.${e}`).join(',')

  const placeholder = computed(() => {
    if (disabled.value) return '暂无可用智能体'
    return streamLoading.value ? '正在回复中...' : '输入消息...'
  })
  // 附件上传完成前不能发送，否则消息中的附件没有地址
  const attachmentsReady = computed(() => fileList.value.every((attachment) => attachment.status === 'success'))
  const canSend = computed(
    () =>
      !disabled.value &&
      (question.value.trim().length > 0 || fileList.value.length > 0) &&
      !streamLoading.value &&
      !sending.value &&
      attachmentsReady.value,
  )

  const imageFiles = computed(() => fileList.value.filter((attachment) => isImage(attachment.name)))

  // 附件上传与本地预览
  const validateFile = (file: File) => fileList.value.length < maxFiles && file.size > 0 && file.size <= maxSizeMB * 1024 * 1024

  const addFile = (file: File) => {
    if (disabled.value || streamLoading.value || sending.value || !validateFile(file)) return
    const attachment: FileItem = reactive({
      uid: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      raw: file,
      status: 'ready',
      progress: 0,
    })
    if (isImage(file.name) || isAudio(file.name) || isVideo(file.name)) {
      attachment.previewUrl = URL.createObjectURL(file)
    }
    fileList.value.push(attachment)
    uploadAttachment(attachment)
  }

  // 原文件重试复用上传流程；移除或切换会话后忽略旧请求的回调。
  const uploadAttachment = (attachment: FileItem) => {
    if (disabled.value || streamLoading.value || sending.value || attachment.status === 'uploading' || !fileList.value.includes(attachment)) return
    attachment.status = 'uploading'
    attachment.progress = 0
    attachment.errMsg = ''
    void Promise.resolve()
      .then(() => {
        if (!fileList.value.includes(attachment)) return
        return uploadFile(attachment.raw, getChatId(), (percent) => {
          if (!fileList.value.includes(attachment)) return
          // 文件传输结束后仍等待服务端处理，成功响应前最多显示 95%。
          attachment.progress = Number.isFinite(percent) ? Math.min(UPLOAD_PROGRESS_PENDING_MAX, Math.max(0, percent)) : 0
        })
      })
      .then((url) => {
        if (!fileList.value.includes(attachment)) return
        const fileId = url?.split(/[?#]/)[0]?.split('/').filter(Boolean).pop()
        if (!url || !fileId) throw new Error('上传未返回文件地址')
        attachment.url = url
        attachment.file_id = fileId
        attachment.progress = 100
        attachment.status = 'success'
      })
      .catch(() => {
        if (!fileList.value.includes(attachment)) return
        attachment.status = 'fail'
        attachment.errMsg = '上传失败'
      })
  }

  const retryFile = (attachment: FileItem) => {
    if (attachment.status === 'fail') uploadAttachment(attachment)
  }

  const addFiles = (files: FileList | File[] | null | undefined) => {
    if (!files || disabled.value) return
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

  // 提交一条新问题；首条消息先在会话列表显示标题，流结束后再保存标题
  const submitQuestion = (message: QuestionMessage, formData?: Dict<unknown>) => {
    const questionText = message.content
    const chatId = getChatId()

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

    sendMessage({
      chatId,
      message,
      newQuestion: true,
      questionContent: { ...message },
      reChat: false,
      formData,
      onComplete: (e) => {
        if (!e && isFirstMessage && questionText) renameChat(chatId, abstract).catch(() => {})
      },
    })
  }

  // 发送输入框内容与暂存附件。附件上传中时 canSend 为 false。
  const send = async () => {
    if (!canSend.value) return
    sending.value = true
    try {
      // 一次遍历完成附件分类，仅提交有附件的字段。
      const message: QuestionMessage = { type: 'QUESTION', content: question.value.trim() }
      for (const attachment of fileList.value) {
        let attachmentKey: MessageAttachmentKey = 'other_list'
        if (isImage(attachment.name)) attachmentKey = 'image_list'
        else if (isDocument(attachment.name)) attachmentKey = 'document_list'
        else if (isAudio(attachment.name)) attachmentKey = 'audio_list'
        else if (isVideo(attachment.name)) attachmentKey = 'video_list'

        const attachments = (message[attachmentKey] ??= [])
        attachments.push({ url: attachment.url, file_id: attachment.file_id, name: attachment.name })
      }

      submitQuestion(message)
      question.value = ''
      clearFiles()
    } catch (e) {
      console.error('send failed:', e)
    } finally {
      sending.value = false
    }
  }

  /** 由开场白、回答中的快捷问题或 HTML 渲染发起提问；不读取也不清空输入框与暂存附件。 */
  const sendQuestion = (content: string, options: QuestionOptions = {}) => {
    if (disabled.value || streamLoading.value || sending.value || !content.trim()) return
    submitQuestion({ ...options.attachments, type: 'QUESTION', content: content.trim() }, options.formData)
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
    appInfo,
    question,
    fileList,
    maxFiles,
    maxSizeMB,
    acceptList,
    streamLoading,
    disabled,
    placeholder,
    canSend,
    imageFiles,
    addFile,
    addFiles,
    removeFile,
    retryFile,
    send,
    sendQuestion,
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

// 供只读场景可选注入：日志等视图不提供输入框，拿不到返回 null
export function useMessageInputStoreOptional(): MessageInputStore | null {
  return inject(MESSAGE_INPUT_KEY, null)
}
