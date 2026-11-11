import { inject, ref, type InjectionKey } from 'vue'
import type { ChatParagraphSource } from '@/api/types'
import type { ChatRecordMeta } from '../core/types'
import { createExecutionDetailStore } from './execution-detail/index'
import { createKnowledgeSourceStore } from './knowledge-source/index'

/** 右侧栏面板：执行详情与知识来源共用同一位置，后打开的替换当前面板。 */
export const RIGHT_SIDEBAR_PANEL = {
  EXECUTION_DETAIL: 'EXECUTION_DETAIL',
  KNOWLEDGE_SOURCE: 'KNOWLEDGE_SOURCE',
} as const

export type RightSidebarPanel = (typeof RIGHT_SIDEBAR_PANEL)[keyof typeof RIGHT_SIDEBAR_PANEL]

/**
 * 右侧栏 store：当前面板与右侧开合，组合各面板自己的 store。
 * 由 view 创建并 provide；消息底部点击「执行详情」「知识来源」时写入对应面板数据并打开右侧。
 */
export function createRightSidebarStore() {
  const panel = ref<RightSidebarPanel>(RIGHT_SIDEBAR_PANEL.EXECUTION_DETAIL)
  const rightSideOpen = ref(false)
  const executionDetail = createExecutionDetailStore()
  const knowledgeSource = createKnowledgeSourceStore()

  const openPanel = (target: RightSidebarPanel) => {
    panel.value = target
    rightSideOpen.value = true
  }

  // 展示执行详情
  const showExecutionDetail = (details: ChatRecordMeta['executionDetails']) => {
    executionDetail.setExecutionDetails(details)
    openPanel(RIGHT_SIDEBAR_PANEL.EXECUTION_DETAIL)
  }

  // 展示回答引用的知识来源分段
  const showKnowledgeSource = (paragraphs: ChatParagraphSource[]) => {
    knowledgeSource.setParagraphs(paragraphs)
    openPanel(RIGHT_SIDEBAR_PANEL.KNOWLEDGE_SOURCE)
  }

  return {
    panel,
    rightSideOpen,
    executionDetail,
    knowledgeSource,
    showExecutionDetail,
    showKnowledgeSource,
    closeRightSide: () => (rightSideOpen.value = false),
  }
}

export type RightSidebarStore = ReturnType<typeof createRightSidebarStore>

export const RIGHT_SIDEBAR_KEY: InjectionKey<RightSidebarStore> = Symbol('right-sidebar')

export function useRightSidebarStore(): RightSidebarStore {
  const store = inject(RIGHT_SIDEBAR_KEY)
  if (!store) throw new Error('useRightSidebarStore 必须在 ConversationView 内使用')
  return store
}
