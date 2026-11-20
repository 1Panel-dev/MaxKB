import { computed, reactive } from 'vue'
import type { SearchCondition } from './types'
import { t } from '@/locales'

export const compareOptions = reactive([
  { value: 'contain' as const, label: computed(() => t('dynamicForm.operators.contain')) },
  { value: 'not_contain' as const, label: computed(() => t('dynamicForm.operators.not_contain')) },
  { value: 'eq' as const, label: computed(() => t('dynamicForm.operators.eq')) },
]) satisfies { value: SearchCondition['compare']; label: string }[]

export const defaultSearchCondition: SearchCondition = { key: '', compare: 'contain', value: '' }
