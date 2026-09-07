import type { KnowledgeItem } from '@/api/types'
import type { NodeSearchScopeData } from '@/workflow-canvas/component/node-search-scope/types'
import type { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'

export interface KnowledgeSearchSetting {
  top_n: number
  similarity: number
  max_paragraph_char_number: number
  search_mode: (typeof KNOWLEDGE_SEARCH_MODE)[keyof typeof KNOWLEDGE_SEARCH_MODE]
}

export interface SearchKnowledgeNodeForm extends NodeSearchScopeData {
  knowledge_id_list: string[]
  knowledge_list: (Partial<KnowledgeItem> & { id: string })[]
  all_knowledge_id_list?: string[]
  knowledge_setting: KnowledgeSearchSetting
  question_reference_address: string[]
  show_knowledge: boolean
}
