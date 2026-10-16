import { KNOWLEDGE_TYPE, KNOWLEDGE_SYNC_TYPE, KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import type { KnowledgeType } from '@/api/types'

/** 知识库图片上传与召回测试共用的格式、文件选择范围和展示文案。 */
export const KNOWLEDGE_IMAGE_EXTENSIONS: readonly string[] = ['JPG', 'JPEG', 'PNG', 'WEBP', 'BMP']
export const KNOWLEDGE_IMAGE_ACCEPT = KNOWLEDGE_IMAGE_EXTENSIONS.map((extension) => `.${extension.toLowerCase()}`).join(',')
export const KNOWLEDGE_IMAGE_TYPE_LABEL = KNOWLEDGE_IMAGE_EXTENSIONS.join('、')

/** 前端知识库类型标识。 */
export const KNOWLEDGE_TYPE_KEY = {
  BASE: 'BASE',
  WEB: 'WEB',
  LARK: 'LARK',
  WORKFLOW: 'WORKFLOW',
} as const

/** 接口数字类型对应的前端语义标识，用于业务判断。 */
export const KNOWLEDGE_TYPE_MAP = {
  [KNOWLEDGE_TYPE.BASE]: KNOWLEDGE_TYPE_KEY.BASE,
  [KNOWLEDGE_TYPE.WEB]: KNOWLEDGE_TYPE_KEY.WEB,
  [KNOWLEDGE_TYPE.LARK]: KNOWLEDGE_TYPE_KEY.LARK,
  [KNOWLEDGE_TYPE.WORKFLOW]: KNOWLEDGE_TYPE_KEY.WORKFLOW,
} as const satisfies Record<KnowledgeType, keyof typeof KNOWLEDGE_TYPE>

/** 前端语义标识对应的展示文案。 */
export const KNOWLEDGE_TYPE_LABELS = {
  [KNOWLEDGE_TYPE_KEY.BASE]: '通用类型',
  [KNOWLEDGE_TYPE_KEY.WEB]: 'web站点类型',
  [KNOWLEDGE_TYPE_KEY.LARK]: '飞书类型',
  [KNOWLEDGE_TYPE_KEY.WORKFLOW]: '工作流类型',
} as const satisfies Record<(typeof KNOWLEDGE_TYPE_MAP)[KnowledgeType], string>

/** 手动同步与定时同步共用的同步方式选项。 */
export const KNOWLEDGE_SYNC_OPTIONS = [
  { value: KNOWLEDGE_SYNC_TYPE.INCREMENTAL, label: '增量同步', description: '跳过未更新的文档，更新有变化的文档，并清理来源中已不存在的文档' },
  { value: KNOWLEDGE_SYNC_TYPE.REPLACE, label: '替换同步', description: '重新获取来源文档并替换匹配的文档，保留未匹配的旧文档' },
  { value: KNOWLEDGE_SYNC_TYPE.COMPLETE, label: '整体同步', description: '重新获取来源文档并重建该来源的文档，保留其他来源的文档' },
] as const

/** 召回测试与工作流知识库检索共用的模式选项。 */
export const KNOWLEDGE_SEARCH_MODE_OPTIONS = [
  {
    value: KNOWLEDGE_SEARCH_MODE.EMBEDDING,
    label: '向量检索',
    description: '向量检索是一种基于向量相似度的检索方式，适用于知识库中的大数据量场景。',
  },
  {
    value: KNOWLEDGE_SEARCH_MODE.KEYWORDS,
    label: '全文检索',
    description: '全文检索是一种基于文本相似度的检索方式，适用于知识库中的小数据量场景。',
  },
  {
    value: KNOWLEDGE_SEARCH_MODE.BLEND,
    label: '混合检索',
    description: '混合检索是一种基于向量和文本相似度的检索方式，适用于知识库中的中等数据量场景。',
  },
] as const
