import { KNOWLEDGE_TYPE } from '@/api/enums'
import type { KnowledgeType } from '@/api/types'

/** 前端知识库类型标识。 */
export const KNOWLEDGE_TYPE_KEY = {
  BASE: 'BASE',
  WEB: 'WEB',
  LARK: 'LARK',
  YUQUE: 'YUQUE',
  WORKFLOW: 'WORKFLOW',
} as const

/** 接口数字类型对应的前端语义标识，用于业务判断。 */
export const KNOWLEDGE_TYPE_MAP = {
  [KNOWLEDGE_TYPE.BASE]: KNOWLEDGE_TYPE_KEY.BASE,
  [KNOWLEDGE_TYPE.WEB]: KNOWLEDGE_TYPE_KEY.WEB,
  [KNOWLEDGE_TYPE.LARK]: KNOWLEDGE_TYPE_KEY.LARK,
  [KNOWLEDGE_TYPE.YUQUE]: KNOWLEDGE_TYPE_KEY.YUQUE,
  [KNOWLEDGE_TYPE.WORKFLOW]: KNOWLEDGE_TYPE_KEY.WORKFLOW,
} as const satisfies Record<KnowledgeType, keyof typeof KNOWLEDGE_TYPE>

/** 前端语义标识对应的展示文案。 */
export const KNOWLEDGE_TYPE_LABELS = {
  [KNOWLEDGE_TYPE_KEY.BASE]: '通用类型',
  [KNOWLEDGE_TYPE_KEY.WEB]: 'web站点类型',
  [KNOWLEDGE_TYPE_KEY.LARK]: '飞书类型',
  [KNOWLEDGE_TYPE_KEY.YUQUE]: '语雀类型',
  [KNOWLEDGE_TYPE_KEY.WORKFLOW]: '工作流类型',
} as const satisfies Record<(typeof KNOWLEDGE_TYPE_MAP)[KnowledgeType], string>
