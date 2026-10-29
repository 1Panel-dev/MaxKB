// 与后端 DocumentSerializers.SplitPattern 的固定标识保持一致；顺序由用户选择决定。
export const splitPatternOptions = [
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
// 分段策略展示文案，配置选项与执行详情共用。
export const DOCUMENT_SPLIT_STRATEGY_LABELS: Readonly<Record<string, string>> = {
  auto: '智能分段（推荐）',
  custom: '高级分段',
  qa: 'QA 问答对',
}
