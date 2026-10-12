import type { ParagraphProblem } from '@/api/types'

/** 新增草稿尚无服务端问题 ID，已有问题保留关联 ID。 */
export type ParagraphQuestionDraft = Pick<ParagraphProblem, 'content'> & { id?: string }
