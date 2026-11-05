import { inject, type InjectionKey, type MaybeRefOrGetter } from 'vue'
import { createShareMessageListStore } from '../../components/share-message-list/index'

export interface SharePanelDeps {
  /** 公开分享链接 ID */
  shareId: MaybeRefOrGetter<string>
}

/**
 * share-panel 组件 store：公开分享页的主面板，组合分享消息列表。
 * 由分享页视图创建并 provide，视图负责在分享 ID 变化时调用 load。
 */
export function createSharePanelStore(deps: SharePanelDeps) {
  const messageList = createShareMessageListStore({ shareId: deps.shareId })
  return { title: messageList.title, messageList, load: messageList.load }
}

export type SharePanelStore = ReturnType<typeof createSharePanelStore>

export const SHARE_PANEL_KEY: InjectionKey<SharePanelStore> = Symbol('share-panel')

export function useSharePanelStore(): SharePanelStore {
  const store = inject(SHARE_PANEL_KEY)
  if (!store) throw new Error('useSharePanelStore 必须在提供 SHARE_PANEL_KEY 的视图内使用')
  return store
}
