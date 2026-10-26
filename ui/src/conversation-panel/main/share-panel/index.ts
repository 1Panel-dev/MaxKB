import { ref, inject, type InjectionKey } from 'vue'

export interface SharePanelDeps {
  /** 提交分享:参数为按消息顺序排列的已选 chat_record id */
  share: (chatRecordIds: string[]) => Promise<unknown> | void
}

/**
 * share-panel 组件 store:分享模式开关 + 已选对话轮次。
 * 由 view 创建并 provide;标题栏分享按钮经 chat-panel 事件交给 view 打开分享模式,view 再用 v-if 切换主区域。
 */
export function createSharePanelStore(deps: SharePanelDeps) {
  const active = ref(false)
  const sharing = ref(false)
  // 已选轮次 key(轮次内提问消息的 id),提交时由面板按消息顺序换算为 chat_record id
  const selectedRoundKeys = ref<string[]>([])

  const open = () => {
    selectedRoundKeys.value = []
    active.value = true
  }
  const close = () => {
    active.value = false
    selectedRoundKeys.value = []
  }

  const isSelected = (roundKey: string) => selectedRoundKeys.value.includes(roundKey)
  const toggleRound = (roundKey: string) => {
    selectedRoundKeys.value = isSelected(roundKey)
      ? selectedRoundKeys.value.filter((selectedKey) => selectedKey !== roundKey)
      : [...selectedRoundKeys.value, roundKey]
  }
  const setSelectedRounds = (roundKeys: string[]) => (selectedRoundKeys.value = [...roundKeys])

  const share = async (chatRecordIds: string[]) => {
    if (!chatRecordIds.length || sharing.value) return
    sharing.value = true
    try {
      await deps.share(chatRecordIds)
      close()
    } finally {
      sharing.value = false
    }
  }

  return { active, sharing, selectedRoundKeys, open, close, isSelected, toggleRound, setSelectedRounds, share }
}

export type SharePanelStore = ReturnType<typeof createSharePanelStore>

export const SHARE_PANEL_KEY: InjectionKey<SharePanelStore> = Symbol('share-panel')

export function useSharePanelStore(): SharePanelStore {
  const store = inject(SHARE_PANEL_KEY)
  if (!store) throw new Error('useSharePanelStore 必须在提供 SHARE_PANEL_KEY 的视图内使用')
  return store
}
