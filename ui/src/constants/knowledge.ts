import type { KnowledgeType } from '@/api/types'
import { KNOWLEDGE_SEARCH_MODE, KNOWLEDGE_SYNC_TYPE, KNOWLEDGE_TYPE } from '@/api/enums'

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

/** 手动同步与定时同步共用的同步方式选项。 */
export const KNOWLEDGE_SYNC_OPTIONS = [
  {
    value: KNOWLEDGE_SYNC_TYPE.INCREMENTAL,
    labelKey: 'knowledge.sync.incremental.label',
    descriptionKey: 'knowledge.sync.incremental.description',
  },
  {
    value: KNOWLEDGE_SYNC_TYPE.REPLACE,
    labelKey: 'knowledge.sync.replace.label',
    descriptionKey: 'knowledge.sync.replace.description',
  },
  {
    value: KNOWLEDGE_SYNC_TYPE.COMPLETE,
    labelKey: 'knowledge.sync.complete.label',
    descriptionKey: 'knowledge.sync.complete.description',
  },
] as const

/** 召回测试、智能体设置与工作流知识库检索共用的模式选项。 */
export const KNOWLEDGE_SEARCH_MODE_OPTIONS = [
  {
    value: KNOWLEDGE_SEARCH_MODE.EMBEDDING,
    labelKey: 'knowledge.retrieval.embedding.label',
    descriptionKey: 'knowledge.retrieval.embedding.description',
  },
  {
    value: KNOWLEDGE_SEARCH_MODE.KEYWORDS,
    labelKey: 'knowledge.retrieval.keywords.label',
    descriptionKey: 'knowledge.retrieval.keywords.description',
  },
  {
    value: KNOWLEDGE_SEARCH_MODE.BLEND,
    labelKey: 'knowledge.retrieval.blend.label',
    descriptionKey: 'knowledge.retrieval.blend.description',
  },
] as const
