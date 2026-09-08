import type { SearchCondition } from './types'

export const compareOptions = [
  { value: 'contain', label: '包含' },
  { value: 'not_contain', label: '不包含' },
  { value: 'eq', label: '等于' },
] satisfies { value: SearchCondition['compare']; label: string }[]

export const defaultSearchCondition: SearchCondition = { key: '', compare: 'contain', value: '' }
