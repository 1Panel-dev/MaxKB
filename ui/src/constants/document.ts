import { computed, reactive } from 'vue'
import { DOCUMENT_HIT_HANDLING } from '@/api/enums'
import { t } from '@/locales'

/** 文档命中处理方式的响应式文案。 */
export const DOCUMENT_HIT_HANDLING_LABELS = reactive({
  [DOCUMENT_HIT_HANDLING.OPTIMIZATION]: computed(() => t('knowledge.document.hitHandling.optimization')),
  [DOCUMENT_HIT_HANDLING.DIRECTLY_RETURN]: computed(() => t('knowledge.document.hitHandling.directlyReturn')),
} as const)

// 与后端 DocumentSerializers.SplitPattern 的固定标识保持一致，供 Agent 识别参数。
export const DOCUMENT_SPLIT_PATTERNS: Readonly<Record<string, string>> = {
  '#': '(?<=^)# .*|(?<=\\n)# .*',
  '##': '(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*',
  '###': '(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*',
  '####': '(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*',
  '#####': '(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*',
  '######': '(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*',
  '-': '(?<! )- .*',
  空格: '(?<! ) (?! )',
  分号: '(?<!；)；(?!；)',
  逗号: '(?<!，)，(?!，)',
  句号: '(?<!。)。(?!。)',
  回车: '(?<!\\n)\\n(?!\\n)',
  空行: '(?<!\\n)\\n\\n(?!\\n)',
}

/** 文档策略和分段节点共用的展示选项，提交正则值。 */
export const DOCUMENT_SPLIT_PATTERN_OPTIONS = reactive([
  { label: '#', value: DOCUMENT_SPLIT_PATTERNS['#']! },
  { label: '##', value: DOCUMENT_SPLIT_PATTERNS['##']! },
  { label: '###', value: DOCUMENT_SPLIT_PATTERNS['###']! },
  { label: '####', value: DOCUMENT_SPLIT_PATTERNS['####']! },
  { label: '#####', value: DOCUMENT_SPLIT_PATTERNS['#####']! },
  { label: '######', value: DOCUMENT_SPLIT_PATTERNS['######']! },
  { label: '-', value: DOCUMENT_SPLIT_PATTERNS['-']! },
  { label: computed(() => t('knowledge.documentStrategy.splitPatterns.space')), value: DOCUMENT_SPLIT_PATTERNS['空格']! },
  { label: computed(() => t('knowledge.documentStrategy.splitPatterns.semicolon')), value: DOCUMENT_SPLIT_PATTERNS['分号']! },
  { label: computed(() => t('knowledge.documentStrategy.splitPatterns.comma')), value: DOCUMENT_SPLIT_PATTERNS['逗号']! },
  { label: computed(() => t('knowledge.documentStrategy.splitPatterns.period')), value: DOCUMENT_SPLIT_PATTERNS['句号']! },
  { label: computed(() => t('knowledge.documentStrategy.splitPatterns.lineBreak')), value: DOCUMENT_SPLIT_PATTERNS['回车']! },
  { label: computed(() => t('knowledge.documentStrategy.splitPatterns.blankLine')), value: DOCUMENT_SPLIT_PATTERNS['空行']! },
])
