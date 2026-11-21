import { computed, inject, reactive, ref, watch } from 'vue'
import { pick } from 'lodash'
import type { ChatMessage, Conversation, ConversationAppInfo, SendMessageOptions } from '../../core/types'
import type { Dict, UrlFileContent } from '@/api/types'
import type { BaseNodeForm, FileUploadSettingData } from '@/workflow-canvas/nodes/base-node/types'
import type { InjectionKey, Ref } from 'vue'
import type { LocationQuery } from 'vue-router'
import { defaultFileUploadSetting } from '@/workflow-canvas/nodes/base-node/constant'
import { URL_FILE_MIME_TYPES, createUrlFile } from './url-upload/index'
import { createUserFormStore } from './user-form/index'
import { AUDIO_EXTENSIONS, DOCUMENT_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS } from '@/constants/file-type'
import { t } from '@/locales'
import { getFileExtension, isAudio, isDocument, isImage, isVideo } from '@/utils/icon'
import { MsgError, MsgWarning } from '@/utils/message'

export interface FileItem {
  uid: number
  name: string
  size: number
  raw?: File
  attachmentType?: MessageAttachmentKey
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
  /** 发送前先截断会话：删除该记录及其之后的对话，如编辑提问；截断失败时不发送。 */
  truncateFromRecordId?: string
}

// 仅注入消息输入所需的会话、上传和发送能力。
export interface MessageInputDeps {
  getUrlFile: (url: string) => Promise<UrlFileContent>
  // 来自 conversation-list
  conversations: Ref<Conversation[]>
  getChatId: () => string
  renameChat: (id: string, name: string) => Promise<void>
  composerResetSignal: Ref<number>
  // 来自 message-list
  messages: Ref<ChatMessage[]>
  /** 截断会话并同步移除对应消息；不提供时不支持发送前截断，提问追加在末尾。 */
  truncateMessages?: (chatRecordId: string) => Promise<void>
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
  const urlUploading = ref(false)

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
    () =>
      (uploadEnabled.value || urlUploadEnabled.value) &&
      !disabled.value &&
      !streamLoading.value &&
      !sending.value &&
      !urlUploading.value &&
      fileList.value.length < maxFiles.value,
  )

  // 语音输入：智能体开启语音转文字且当前模式提供接口时可用
  const transcribing = ref(false)
  const speechEnabled = computed(() => !!deps.speechToText && !!appInfo.value?.stt_model_enable)

  const placeholder = computed(() => {
    if (disabled.value) return t('portal.noAvailableApplications')
    if (transcribing.value) return t('chat.voice.transcribing')
    return streamLoading.value ? t('chat.message.replying') : t('chat.message.inputPlaceholder')
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
      !urlUploading.value &&
      attachmentsReady.value,
  )

  const imageFiles = computed(() =>
    fileList.value.filter((attachment) => attachment.attachmentType === 'image_list' || (!attachment.attachmentType && isImage(attachment.name))),
  )

  // URL 上传：服务端读取远程文件，校验后按类型保留地址或转为本地上传。
  const urlUploadTypes = computed(() =>
    [
      { enabled: uploadSetting.value.document, value: 'document_list' as const, label: t('upload.types.document') },
      { enabled: uploadSetting.value.image, value: 'image_list' as const, label: t('upload.types.image') },
      { enabled: uploadSetting.value.audio, value: 'audio_list' as const, label: t('upload.types.audio') },
      { enabled: uploadSetting.value.video, value: 'video_list' as const, label: t('upload.types.video') },
      { enabled: uploadSetting.value.other, value: 'other_list' as const, label: t('common.labels.other') },
    ].filter((type) => type.enabled),
  )
  const addUrls = async (addresses: string[], attachmentType: MessageAttachmentKey): Promise<boolean> => {
    if (
      !addresses.length ||
      urlUploading.value ||
      !urlUploadEnabled.value ||
      !canUpload.value ||
      !urlUploadTypes.value.some((type) => type.value === attachmentType)
    )
      return false
    if (fileList.value.length + addresses.length > maxFiles.value) {
      MsgWarning(t('chat.upload.countLimitMessage', { count: maxFiles.value }, maxFiles.value))
      return false
    }
    const validAddresses = addresses.filter((address) => {
      try {
        return ['http:', 'https:'].includes(new URL(address).protocol)
      } catch {
        return false
      }
    })
    if (validAddresses.length !== addresses.length) MsgWarning(t('chat.urlUpload.invalidAddressMessage'))
    if (!validAddresses.length) return false
    const extensions =
      attachmentType === 'image_list'
        ? IMAGE_EXTENSIONS
        : attachmentType === 'document_list'
          ? DOCUMENT_EXTENSIONS
          : attachmentType === 'audio_list'
            ? AUDIO_EXTENSIONS
            : attachmentType === 'video_list'
              ? VIDEO_EXTENSIONS
              : (uploadSetting.value.otherExtensions ?? [])
    const expectedMimes = extensions.flatMap((extension) => URL_FILE_MIME_TYPES[extension.toLowerCase()] ?? [])
    // 先占用附件名额，避免并发上传超限，也阻止校验完成前发送。
    const attachments = validAddresses.map((address) =>
      reactive<FileItem>({
        uid: Date.now() + Math.random(),
        name: new URL(address).pathname.split('/').filter(Boolean).pop() || `file_${Date.now()}`,
        size: 0,
        url: address,
        attachmentType,
        status: 'uploading',
        progress: 0,
      }),
    )
    fileList.value.push(...attachments)
    urlUploading.value = true
    try {
      const results = await Promise.all(
        attachments.map(async (attachment) => {
          try {
            const response = await deps.getUrlFile(attachment.url!)
            if (!fileList.value.includes(attachment)) return false
            if (response.status_code !== 200) throw new Error(t('chat.urlUpload.invalidResponseMessage'))
            const mime = (response['Content-Type'] || '').split(';')[0]!.trim().toLowerCase()
            if (expectedMimes.length && !expectedMimes.includes(mime)) throw new Error(t('chat.urlUpload.typeMismatchMessage'))
            const size = Number(response['Content-Length']) || 0
            if (size > maxSizeMB.value * 1024 * 1024) throw new Error(t('chat.upload.sizeLimitMessage', { size: maxSizeMB.value }))
            if (!attachment.name.includes('.')) {
              const extension =
                extensions.find((extension) => URL_FILE_MIME_TYPES[extension.toLowerCase()] === mime) ??
                Object.keys(URL_FILE_MIME_TYPES).find((extension) => URL_FILE_MIME_TYPES[extension] === mime)
              if (extension) attachment.name += `.${extension.toLowerCase()}`
            }
            attachment.size = size
            if (attachmentType === 'document_list' || attachmentType === 'audio_list' || attachmentType === 'other_list') {
              const file = createUrlFile(response.content, attachment.name, mime)
              if (file.size > maxSizeMB.value * 1024 * 1024) throw new Error(t('chat.upload.sizeLimitMessage', { size: maxSizeMB.value }))
              if (!file.size) throw new Error(t('upload.emptyFileMessage'))
              attachment.raw = file
              attachment.size = file.size
              attachment.url = undefined
              attachment.status = 'ready'
              await uploadAttachment(attachment)
              return fileList.value.some((file) => file.uid === attachment.uid && file.status === 'success')
            }
            attachment.status = 'success'
            attachment.progress = 100
            return true
          } catch (error) {
            const index = fileList.value.indexOf(attachment)
            if (index >= 0) {
              removeFile(index)
              MsgWarning(`${attachment.url || attachment.name}：${error instanceof Error ? error.message : t('chat.urlUpload.readFailedMessage')}`)
            }
            return false
          }
        }),
      )
      return results.some(Boolean)
    } finally {
      urlUploading.value = false
    }
  }

  // 附件上传与本地预览
  /** 校验单个文件，返回不通过的提示；拖拽、粘贴不受 accept 限制，需校验扩展名。 */
  const getFileError = (file: File) => {
    if (fileList.value.length >= maxFiles.value) return t('chat.upload.countLimitMessage', { count: maxFiles.value }, maxFiles.value)
    if (!allowedExtensions.value.includes(getFileExtension(file.name))) return t('chat.upload.unsupportedTypeMessage')
    if (file.size <= 0) return t('upload.emptyFileMessage')
    if (file.size > maxSizeMB.value * 1024 * 1024) return t('chat.upload.sizeLimitMessage', { size: maxSizeMB.value })
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
    return Promise.resolve()
      .then(() => {
        if (!fileList.value.includes(attachment)) return
        if (!attachment.raw) return
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
        MsgError(t('upload.status.uploadFailed'))
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
    const conversation = conversations.value.find((item) => item.id === chatId)
    if (isFirstMessage && !conversation) {
      // 本地新会话尚未由历史接口返回，使用首次发送时间展示相对时间。
      const createTime = new Date().toISOString()
      conversations.value.unshift({
        id: chatId,
        abstract: questionText ? abstract : t('chat.defaultConversationTitle'),
        create_time: createTime,
        update_time: createTime,
      })
    } else if (conversation) {
      // 在已有会话中继续提问：移到历史列表顶部并刷新更新时间，与后端按 update_time 倒序展示一致。
      conversation.update_time = new Date().toISOString()
      const index = conversations.value.indexOf(conversation)
      if (index > 0) {
        conversations.value.splice(index, 1)
        conversations.value.unshift(conversation)
      }
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
        if (attachment.attachmentType) attachmentKey = attachment.attachmentType
        else if (isImage(attachment.name)) attachmentKey = 'image_list'
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
        if (!text) return MsgError(t('chat.voice.emptyTranscriptMessage'))
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
    // 校验与截断期间占用发送状态，避免连续触发时重复提交
    sending.value = true
    userForm
      .validate()
      .then(async () => {
        if (options.truncateFromRecordId) {
          // 截断期间新建或切换了会话时放弃发送，避免提问发到其他会话
          const resetSignal = composerResetSignal.value
          await deps.truncateMessages?.(options.truncateFromRecordId)
          if (resetSignal !== composerResetSignal.value) return
        }
        submitQuestion({ ...options.attachments, type: 'QUESTION', content: content.trim() }, options.formData)
      })
      // 校验失败由表单提示，截断失败由请求层提示，均不发送
      .catch(() => {})
      .finally(() => (sending.value = false))
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
    urlUploadTypes,
    urlUploading,
    addUrls,
    canUpload,
    maxFiles,
    maxSizeMB,
    allowedExtensions,
    acceptList,
    streamLoading,
    sending,
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
