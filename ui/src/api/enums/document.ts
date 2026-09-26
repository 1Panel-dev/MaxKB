/** 文档命中处理方式。 */
export const DOCUMENT_HIT_HANDLING = { OPTIMIZATION: 'optimization', DIRECTLY_RETURN: 'directly_return' } as const

/** 文档任务状态，使用文件状态协议中的字符值。 */
export const DOCUMENT_TASK_STATE = { PENDING: '0', STARTED: '1', SUCCESS: '2', FAILURE: '3' } as const

/** 文档状态字符串中各任务的位置。 */
export const DOCUMENT_TASK_TYPE = { EMBEDDING: 1, GENERATE_PROBLEM: 2, SYNC: 3, TOKENIZE: 4 } as const
