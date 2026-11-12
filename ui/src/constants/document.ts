import { DOCUMENT_HIT_HANDLING } from '@/api/enums'

/** 文档命中处理方式的展示文案。 */
export const DOCUMENT_HIT_HANDLING_LABELS = {
  [DOCUMENT_HIT_HANDLING.OPTIMIZATION]: '模型优化',
  [DOCUMENT_HIT_HANDLING.DIRECTLY_RETURN]: '直接回答',
} as const

// 与后端 DocumentSerializers.SplitPattern 的固定标识保持一致；顺序由用户选择决定。
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
    value: '(?<! ) (?! )',
  },
  {
    label: '分号',
    value: '(?<!；)；(?!；)',
  },
  {
    label: '逗号',
    value: '(?<!，)，(?!，)',
  },
  {
    label: '句号',
    value: '(?<!。)。(?!。)',
  },
  {
    label: '回车',
    value: '(?<!\\n)\\n(?!\\n)',
  },
  {
    label: '空行',
    value: '(?<!\\n)\\n\\n(?!\\n)',
  },
]
