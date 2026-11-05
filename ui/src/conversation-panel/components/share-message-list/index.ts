import { computed, inject, ref, toValue, type InjectionKey, type MaybeRefOrGetter } from 'vue'
import ConversationApi from '@/api/chat/conversation'
import type { ChatShareDetail } from '@/api/types'
import type { ChatMessage } from '../../core/types'

export interface ShareMessageListDeps {
  /** 公开分享链接 ID */
  shareId: MaybeRefOrGetter<string>
}

/**
 * 分享消息列表 store：按分享 ID 请求公开分享接口，转换为只读消息。
 * 公开接口按时间正序一次返回全部记录，不请求原会话，也不分页加载历史。
 */
export function createShareMessageListStore(deps: ShareMessageListDeps) {
  const detail = ref<ChatShareDetail | null>(null)
  const loading = ref(false)
  const failed = ref(false)

  const title = computed(() => detail.value?.abstract || '分享对话')
  const messages = computed<ChatMessage[]>(() =>
    (detail.value?.chat_record_list ?? []).flatMap((record): ChatMessage[] => [
      { id: `${record.id}_USER`, role: 'USER', content: record.question ? [record.question] : [] },
      { id: `${record.id}_ASSISTANT`, role: 'ASSISTANT', content: record.messages ?? [], recordId: record.id },
    ]),
  )

  // 切换分享 ID 后旧请求晚到时丢弃
  const load = async () => {
    const shareId = toValue(deps.shareId)
    detail.value = null
    failed.value = false
    if (!shareId) return
    loading.value = true
    try {
      const shareDetail = await ConversationApi.getShareConversation(shareId)
      if (shareId === toValue(deps.shareId)) detail.value = shareDetail
    } catch {
      if (shareId === toValue(deps.shareId)) failed.value = true
    } finally {
      if (shareId === toValue(deps.shareId)) loading.value = false
    }
  }

  return { title, messages, loading, failed, load }
}

export type ShareMessageListStore = ReturnType<typeof createShareMessageListStore>

export const SHARE_MESSAGE_LIST_KEY: InjectionKey<ShareMessageListStore> = Symbol('share-message-list')

export function useShareMessageListStore(): ShareMessageListStore {
  const store = inject(SHARE_MESSAGE_LIST_KEY)
  if (!store) throw new Error('useShareMessageListStore 必须在提供 SHARE_MESSAGE_LIST_KEY 的组件内使用')
  return store
}
