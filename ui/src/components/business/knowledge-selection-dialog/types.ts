import type { KnowledgeItem } from '@/api/types'

/** 已选知识库允许只保留 ID，避免旧工作流缺少快照时丢失关联。 */
export type KnowledgeSelection = Pick<KnowledgeItem, 'id'> & Partial<KnowledgeItem>
