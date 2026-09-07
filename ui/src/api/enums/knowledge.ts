/** 后端知识库类型。 */
export const KNOWLEDGE_TYPE = { BASE: 0, WEB: 1, LARK: 2, YUQUE: 3, WORKFLOW: 4 } as const

/** 知识库分段检索模式。 */
export const KNOWLEDGE_SEARCH_MODE = { EMBEDDING: 'embedding', KEYWORDS: 'keywords', BLEND: 'blend' } as const
