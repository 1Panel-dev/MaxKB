import type { KnowledgeItem, KnowledgeTagGroup } from '@/api/types'
import type { NodeSearchScopeData } from '@/workflow-canvas/component/node-search-scope/types'

export interface SearchCondition {
  key: string
  compare: 'contain' | 'not_contain' | 'eq'
  value: string
}

export interface SearchDocumentForm extends NodeSearchScopeData {
  knowledge_id_list: string[]
  knowledge_list: (Partial<KnowledgeItem> & { id: string })[]
  search_mode: 'auto' | 'custom'
  question_reference: string[]
  search_condition_type: 'AND' | 'OR'
  search_condition_list: SearchCondition[]
  knowledge_tags: KnowledgeTagGroup[]
}
