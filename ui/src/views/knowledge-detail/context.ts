/** 知识库详情容器与子页面共享已加载的详情及保存后的更新能力。 */
import { inject, type ComputedRef, type InjectionKey } from 'vue'
import type { KnowledgeDetail } from '@/api/types'

interface KnowledgeDetailContext {
  knowledge: ComputedRef<KnowledgeDetail | undefined>
  replaceKnowledgeDetail: (knowledge: KnowledgeDetail) => void
}

export const knowledgeDetailContextKey: InjectionKey<KnowledgeDetailContext> = Symbol('knowledge-detail-context')

export function useKnowledgeDetailContext() {
  const context = inject(knowledgeDetailContextKey)
  if (!context) throw new Error('Knowledge detail context is unavailable')
  return context
}
