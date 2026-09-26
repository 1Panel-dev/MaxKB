import { DOCUMENT_HIT_HANDLING } from '@/api/enums'

/** 文档命中处理方式的展示文案。 */
export const DOCUMENT_HIT_HANDLING_LABELS = {
  [DOCUMENT_HIT_HANDLING.OPTIMIZATION]: '模型优化',
  [DOCUMENT_HIT_HANDLING.DIRECTLY_RETURN]: '直接回答',
} as const
