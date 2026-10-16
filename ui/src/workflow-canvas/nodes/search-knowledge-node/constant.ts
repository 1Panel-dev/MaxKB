import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import type { KnowledgeSearchSetting } from './types'

export const defaultSearchSetting: KnowledgeSearchSetting = {
  top_n: 3,
  similarity: 0.6,
  max_paragraph_char_number: 5000,
  search_mode: KNOWLEDGE_SEARCH_MODE.EMBEDDING,
}
