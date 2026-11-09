import { ref, computed, reactive, watch, inject, type Ref, type InjectionKey } from 'vue'
import type { LocationQuery } from 'vue-router'
import { pick } from 'lodash'
import { IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS } from '@/constants/file-type'
import { isImage, isDocument, isAudio, isVideo, getFileExtension } from '@/utils/icon'
import { MsgError, MsgWarning } from '@/utils/message'
import type { Dict } from '@/api/types'
import { defaultFileUploadSetting } from '@/workflow-canvas/nodes/base-node/constant'
import type { BaseNodeForm, FileUploadSettingData } from '@/workflow-canvas/nodes/base-node/types'
import type { ChatMessage, Conversation, ConversationAppInfo, SendMessageOptions } from '../../core/types'
import { createUserFormStore } from './user-form/index'

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
  /** 语音转文字，表单字段 file 为录音文件；不传时不显示语音输入。 */
  speechToText?: (data: FormData) => Promise<unknown>
  /** 当前智能体信息：只读，由 view 加载维护。 */
  appInfo: Readonly<Ref<ConversationAppInfo | null>>
  /** 禁用输入与发送，如门户没有可用智能体时；不传时始终可用。 */
  disabled?: Readonly<Ref<boolean>>
  /** 是否在用户输入表单中编辑接口传参，仅调试对话开启。 */
  apiInputEditable?: boolean
  /** 地址栏参数，接口传参不可编辑时优先使用，缺省时用默认值。 */
  getRouteQuery?: () => LocationQuery
}

// 上传请求返回前进度条的最大值
const UPLOAD_PROGRESS_PENDING_MAX = 95

/**
 * message-input 组件 store:本组件独有——输入内容 + 暂存文件 + 发送。
 */
export function createMessageInputStore(deps: MessageInputDeps) {
  const { conversations, getChatId, renameChat, composerResetSignal, messages, streamLoading, sendMessage, uploadFile, stop, appInfo } = deps
  const disabled = computed(() => deps.disabled?.value ?? false)
  const userForm = createUserFormStore({ appInfo, apiInputEditable: deps.apiInputEditable ?? false, getRouteQuery: deps.getRouteQuery })

  // 输入状态与附件限制
  const question = ref('')
  const fileList = ref<FileItem[]>([])
  const sending = ref(false)

  // 文件上传配置：优先读取开始节点，缺失时回退到智能体字段，再补齐默认值。
  const baseNodeData = computed(() => {
    const baseNode = appInfo.value?.work_flow?.nodes?.find((node) => node.id === 'base-node')
    return (baseNode?.properties?.node_data ?? {}) as Partial<Pick<BaseNodeForm, 'file_upload_enable' | 'file_upload_setting'>>
  })
  const uploadSetting = computed<FileUploadSettingData>(() => ({
    ...defaultFileUploadSetting,
    ...(baseNodeData.value.file_upload_setting ?? (appInfo.value?.file_upload_setting as Partial<FileUploadSettingData> | undefined)),
  }))
  const fileUploadEnabled = computed(() => Boolean(baseNodeData.value.file_upload_enable ?? appInfo.value?.file_upload_enable))
  /** 本地上传：控制上传按钮、拖拽与粘贴入口。 */
  const uploadEnabled = computed(() => fileUploadEnabled.value && uploadSetting.value.local_upload)
  // TODO: URL 上传入口未实现，页面接入时使用 urlUploadEnabled 控制显示，并复用数量、大小、类型限制。
  const urlUploadEnabled = computed(() => fileUploadEnabled.value && uploadSetting.value.url_upload)
  const maxFiles = computed(() => uploadSetting.value.maxFiles)
  const maxSizeMB = computed(() => uploadSetting.value.fileLimit)
  /** 允许上传的大写扩展名：按勾选的文件类型拼接，其他文件使用自定义扩展名。 */
  const allowedExtensions = computed(() => {
    const { image, document, audio, video, other, otherExtensions } = uploadSetting.value
    const extensions = [
      ...(image ? IMAGE_EXTENSIONS : []),
      ...(document ? DOCUMENT_EXTENSIONS : []),
      ...(audio ? AUDIO_EXTENSIONS : []),
      ...(video ? VIDEO_EXTENSIONS : []),
      ...(other ? (otherExtensions ?? []).map((extension) => extension.toUpperCase()) : []),
    ]
    return [...new Set(extensions)]
  })
  const acceptList = computed(() => allowedExtensions.value.map((extension) => `.${extension}`).join(','))
  const canUpload = computed(
    () => uploadEnabled.value && !disabled.value && !streamLoading.value && !sending.value && fileList.value.length < maxFiles.value,
  )

  // 语音输入：智能体开启语音转文字且当前模式提供接口时可用
  const transcribing = ref(false)
  const speechEnabled = computed(() => !!deps.speechToText && !!appInfo.value?.stt_model_enable)

  const placeholder = computed(() => {
    if (disabled.value) return '暂无可用智能体'
    if (transcribing.value) return '语音转文字中...'
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
      !transcribing.value &&
      attachmentsReady.value,
  )

  const imageFiles = computed(() => fileList.value.filter((attachment) => isImage(attachment.name)))

  // 附件上传与本地预览
  /** 校验单个文件，返回不通过的提示；拖拽、粘贴不受 accept 限制，需校验扩展名。 */
  const getFileError = (file: File) => {
    if (fileList.value.length >= maxFiles.value) return `单次最多上传 ${maxFiles.value} 个文件`
    if (!allowedExtensions.value.includes(getFileExtension(file.name))) return '不支持上传该类型的文件'
    if (file.size <= 0) return '不能上传空文件'
    if (file.size > maxSizeMB.value * 1024 * 1024) return `每个文件不能超过 ${maxSizeMB.value}MB`
  }

  /** 添加并上传文件，校验不通过时返回提示。 */
  const addFile = (file: File): string | undefined => {
    if (!uploadEnabled.value || disabled.value || streamLoading.value || sending.value) return
    const error = getFileError(file)
    if (error) return error
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

  // 移除或切换会话后忽略旧请求的回调。
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
      .catch((error: unknown) => {
        const index = fileList.value.indexOf(attachment)
        if (index < 0) return
        removeFile(index)
        MsgError('上传失败')
      })
  }

  const addFiles = (files: FileList | File[] | null | undefined) => {
    if (!files || disabled.value) return
    // 批量添加时相同提示只显示一次
    const errors = new Set<string>()
    Array.from(files).forEach((file) => {
      const error = addFile(file)
      if (error) errors.add(error)
    })
    errors.forEach((error) => MsgWarning(error))
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
      formData: { ...userForm.getFormData(), ...formData },
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
      // 用户输入参数校验失败时由表单提示，保留输入内容与附件
      const formValid = await userForm.validate().then(
        () => true,
        () => false,
      )
      if (!formValid) return
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

  /** 录音转写后追加到输入框；智能体开启自动发送时直接发送。切换会话后丢弃旧结果。 */
  const transcribe = (audio: Blob) => {
    if (!deps.speechToText || transcribing.value) return
    const resetSignal = composerResetSignal.value
    const formData = new FormData()
    formData.append('file', audio, 'recording.mp3')
    transcribing.value = true
    deps
      .speechToText(formData)
      .then((result) => {
        if (resetSignal !== composerResetSignal.value) return
        const text = typeof result === 'string' ? result.trim() : ''
        if (!text) return MsgError('未识别到语音内容')
        question.value = question.value ? `${question.value} ${text}` : text
        transcribing.value = false
        if (appInfo.value?.stt_autosend) void send()
      })
      .catch(() => {})
      .finally(() => {
        transcribing.value = false
      })
  }

  /** 由开场白、回答中的快捷问题或 HTML 渲染发起提问；不读取也不清空输入框与暂存附件。 */
  const sendQuestion = (content: string, options: QuestionOptions = {}) => {
    if (disabled.value || streamLoading.value || sending.value || !content.trim()) return
    userForm
      .validate()
      .then(() => submitQuestion({ ...options.attachments, type: 'QUESTION', content: content.trim() }, options.formData))
      .catch(() => {})
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
    userForm,
    question,
    fileList,
    uploadEnabled,
    urlUploadEnabled,
    canUpload,
    maxFiles,
    maxSizeMB,
    allowedExtensions,
    acceptList,
    streamLoading,
    disabled,
    placeholder,
    canSend,
    speechEnabled,
    transcribing,
    transcribe,
    imageFiles,
    addFile,
    addFiles,
    removeFile,
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

const ATTACHMENT_FIELDS = ['image_list', 'document_list', 'audio_list', 'video_list', 'other_list']

/**
 * 回复内容（快捷问题、HTML、iframe）内的提问入口：otherParams 为 v2 的 other_params_data（附件列表与 form_data）。
 * 发送走 message-input，新对话时由它生成会话并同步标题；日志等只读视图拿不到 store，返回 null。
 */
export function useSendQuestionOptional(): ((question: string, otherParams?: Dict<unknown>) => void) | null {
  const store = useMessageInputStoreOptional()
  if (!store) return null
  return (question, otherParams) =>
    store.sendQuestion(question, {
      attachments: pick(otherParams, ATTACHMENT_FIELDS) as QuestionOptions['attachments'],
      formData: otherParams?.form_data as Dict<unknown> | undefined,
    })
}
