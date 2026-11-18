import { DOCUMENT_HIT_HANDLING } from '@/api/enums'

/** 文档命中处理方式的翻译键。 */
export const DOCUMENT_HIT_HANDLING_MESSAGE_KEYS = {
  [DOCUMENT_HIT_HANDLING.OPTIMIZATION]: 'knowledge.document.hitHandling.optimization',
  [DOCUMENT_HIT_HANDLING.DIRECTLY_RETURN]: 'knowledge.document.hitHandling.directlyReturn',
} as const

// 与后端 DocumentSerializers.SplitPattern 的固定标识保持一致；顺序由用户选择决定。
// label 保留供工作流 Agent 识别参数；界面优先翻译 labelKey，纯符号直接展示 label。
export const DOCUMENT_SPLIT_PATTERN_OPTIONS = [
  {
    label: '#',
    value: '(?<=^)# .*|(?<=\\n)# .*',
  },
  {
    label: '##',
    value: '(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*',
  },
  {
    label: '###',
    value: '(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*',
  },
  {
    label: '####',
    value: '(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*',
  },
  {
    label: '#####',
    value: '(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*',
  },
  {
    label: '######',
    value: '(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*',
  },
  {
    label: '-',
    value: '(?<! )- .*',
  },
  {
    label: '空格',
    labelKey: 'knowledge.documentStrategy.splitPatterns.space',
    value: '(?<! ) (?! )',
  },
  {
    label: '分号',
    labelKey: 'knowledge.documentStrategy.splitPatterns.semicolon',
    value: '(?<!；)；(?!；)',
  },
  {
    label: '逗号',
    labelKey: 'knowledge.documentStrategy.splitPatterns.comma',
    value: '(?<!，)，(?!，)',
  },
  {
    label: '句号',
    labelKey: 'knowledge.documentStrategy.splitPatterns.period',
    value: '(?<!。)。(?!。)',
  },
  {
    label: '回车',
    labelKey: 'knowledge.documentStrategy.splitPatterns.lineBreak',
    value: '(?<!\\n)\\n(?!\\n)',
  },
  {
    label: '空行',
    labelKey: 'knowledge.documentStrategy.splitPatterns.blankLine',
    value: '(?<!\\n)\\n\\n(?!\\n)',
  },
]
