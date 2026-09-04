import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import type { KnowledgeSearchSetting } from './types'

export const defaultSearchSetting: KnowledgeSearchSetting = {
  top_n: 3,
  similarity: 0.6,
  max_paragraph_char_number: 5000,
  search_mode: KNOWLEDGE_SEARCH_MODE.EMBEDDING,
}

export const searchModeOptions = [
  { value: KNOWLEDGE_SEARCH_MODE.EMBEDDING, label: '向量检索', description: '基于向量相似度检索，适用于知识库中的大数据量场景。' },
  { value: KNOWLEDGE_SEARCH_MODE.KEYWORDS, label: '全文检索', description: '基于文本相似度检索，适用于知识库中的小数据量场景。' },
  { value: KNOWLEDGE_SEARCH_MODE.BLEND, label: '混合检索', description: '结合向量和文本相似度检索，适用于知识库中的中等数据量场景。' },
]
