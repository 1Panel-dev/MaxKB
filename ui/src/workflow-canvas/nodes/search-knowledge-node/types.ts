import type { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import type { KnowledgeSelection } from '@/components/business/knowledge-selection-dialog/types'

export interface KnowledgeSearchSetting {
  top_n: number
  similarity: number
  max_paragraph_char_number: number
  search_mode: (typeof KNOWLEDGE_SEARCH_MODE)[keyof typeof KNOWLEDGE_SEARCH_MODE]
}

export interface SearchKnowledgeNodeForm {
  knowledge_id_list: string[]
  knowledge_list: KnowledgeSelection[]
  all_knowledge_id_list?: string[]
  knowledge_setting: KnowledgeSearchSetting
  question_reference_address: string[]
  show_knowledge: boolean
  search_scope_type: 'custom' | 'referencing'
  search_scope_source: 'knowledge' | 'document'
  search_scope_reference: string[]
}
