import { computed, inject, ref, type InjectionKey, type Ref } from 'vue'
import type { ChatMessage } from '../../../core/types'
import { VIEW_TYPE, type ViewType } from '../../../view/index'

/** 提供分享服务的视图；其他视图不显示进入分享选择的入口。 */
export const SHAREABLE_VIEWS: readonly ViewType[] = [VIEW_TYPE.CHAT, VIEW_TYPE.PORTAL]

export interface ShareLinkDeps {
  /** 当前会话消息：只读，由消息列表 Store 维护 */
  messages: Readonly<Ref<ChatMessage[]>>
  /** 创建分享链接：参数为按消息顺序排列的已选 chat_record id */
  share: (chatRecordIds: string[]) => Promise<unknown> | void
  /** 开关分享模式；开关由会话列表 Store 的 isShared 维护 */
  setShared: (shared: boolean) => void
}

/**
 * 分享链接 store：正式对话消息列表分享选择态的记录 ID、选择操作、提交与退出。
 * 由 chat / portal 视图创建并 provide；分享组件只负责展示。
 */
export function createShareLinkStore(deps: ShareLinkDeps) {
  const { messages } = deps
  const sharing = ref(false)
  // 已选 chat_record id；提问与回答共用记录 ID，按整轮选择
  const selectedRecordIds = ref<string[]>([])

  // 每条消息对应的记录 ID：提问取下一条回答的记录 ID，无记录 ID 的问答不可选
  const messageRecordIds = computed(() =>
    messages.value.map((message, index) => (message.role === 'ASSISTANT' ? message.recordId : messages.value[index + 1]?.recordId)),
  )
  const availableRecordIds = computed(() => [...new Set(messageRecordIds.value.filter((id): id is string => Boolean(id)))])

  // 全选与数量仅统计当前列表中的可分享记录
  const selectedIds = computed(() => availableRecordIds.value.filter((recordId) => selectedRecordIds.value.includes(recordId)))
  const selectedCount = computed(() => selectedIds.value.length)
  const totalCount = computed(() => availableRecordIds.value.length)
  const allSelected = computed(() => totalCount.value > 0 && selectedCount.value === totalCount.value)
  const partiallySelected = computed(() => selectedCount.value > 0 && !allSelected.value)

  const isSelected = (recordId?: string) => Boolean(recordId && selectedRecordIds.value.includes(recordId))
  const isDisabled = (recordId?: string) => !recordId || sharing.value

  const toggle = (recordId?: string) => {
    if (!recordId || isDisabled(recordId)) return
    selectedRecordIds.value = isSelected(recordId)
      ? selectedRecordIds.value.filter((selectedId) => selectedId !== recordId)
      : [...selectedRecordIds.value, recordId]
  }
  const selectAll = (checked: boolean | string | number) => {
    if (sharing.value) return
    selectedRecordIds.value = checked ? [...availableRecordIds.value] : []
  }

  // 进入分享选择：以传入记录为初始勾选，仅保留当前可分享记录，空值与重复项忽略
  const enterShare = (recordIds: (string | undefined)[] = []) => {
    selectedRecordIds.value = availableRecordIds.value.filter((recordId) => recordIds.includes(recordId))
    deps.setShared(true)
  }

  // 退出分享选择：清空已选记录并关闭分享模式
  const exitShare = () => {
    selectedRecordIds.value = []
    deps.setShared(false)
  }

  // 创建并复制链接：成功后退出，失败时保留选择供重试
  const copyShareLink = async () => {
    if (!selectedCount.value || sharing.value) return
    sharing.value = true
    try {
      await deps.share(selectedIds.value)
      exitShare()
    } catch {
      /* 失败提示由请求层处理 */
    } finally {
      sharing.value = false
    }
  }

  return {
    sharing,
    messageRecordIds,
    selectedCount,
    totalCount,
    allSelected,
    partiallySelected,
    isSelected,
    isDisabled,
    toggle,
    selectAll,
    enterShare,
    exitShare,
    copyShareLink,
  }
}

export type ShareLinkStore = ReturnType<typeof createShareLinkStore>

export const SHARE_LINK_KEY: InjectionKey<ShareLinkStore> = Symbol('share-link')

/** 消息所属问答轮次的记录 ID，由 ShareMessageRow 提供给消息内容，供内容项的分享入口预先勾选。 */
export const SHARE_RECORD_ID_KEY: InjectionKey<Readonly<Ref<string | undefined>>> = Symbol('share-record-id')

/** 未提供时为 undefined，分享入口不预先勾选。 */
export function useShareRecordId(): Readonly<Ref<string | undefined>> {
  return inject(SHARE_RECORD_ID_KEY, ref(undefined))
}

/** 未提供时返回 null，分享组件不可选择与提交。 */
export function useShareLinkStoreOptional(): ShareLinkStore | null {
  return inject(SHARE_LINK_KEY, null)
}
