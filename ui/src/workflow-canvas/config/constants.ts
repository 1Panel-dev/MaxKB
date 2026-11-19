import { computed, reactive } from 'vue'
import { t } from '@/locales'

// 比较符协议值保持固定，展示名称按当前语言读取。
export const compareList = reactive([
  { value: 'is_null', label: computed(() => t('dynamicForm.operators.is_null')) },
  { value: 'is_not_null', label: computed(() => t('dynamicForm.operators.is_not_null')) },
  { value: 'contain', label: computed(() => t('dynamicForm.operators.contain')) },
  { value: 'not_contain', label: computed(() => t('dynamicForm.operators.not_contain')) },
  { value: 'eq', label: computed(() => t('dynamicForm.operators.eq')) },
  { value: 'not_eq', label: computed(() => t('dynamicForm.operators.not_eq')) },
  { value: 'ge', label: computed(() => t('dynamicForm.operators.ge')) },
  { value: 'gt', label: computed(() => t('dynamicForm.operators.gt')) },
  { value: 'le', label: computed(() => t('dynamicForm.operators.le')) },
  { value: 'lt', label: computed(() => t('dynamicForm.operators.lt')) },
  { value: 'len_eq', label: computed(() => t('dynamicForm.operators.len_eq')) },
  { value: 'len_ge', label: computed(() => t('dynamicForm.operators.len_ge')) },
  { value: 'len_gt', label: computed(() => t('dynamicForm.operators.len_gt')) },
  { value: 'len_le', label: computed(() => t('dynamicForm.operators.len_le')) },
  { value: 'len_lt', label: computed(() => t('dynamicForm.operators.len_lt')) },
  { value: 'is_true', label: computed(() => t('dynamicForm.operators.is_true')) },
  { value: 'is_not_true', label: computed(() => t('dynamicForm.operators.is_not_true')) },
  { value: 'start_with', label: computed(() => t('dynamicForm.operators.start_with')) },
  { value: 'end_with', label: computed(() => t('dynamicForm.operators.end_with')) },
  { value: 'regex', label: computed(() => t('dynamicForm.operators.regex')) },
  { value: 'wildcard', label: computed(() => t('dynamicForm.operators.wildcard')) },
])

export const START_NODE_REFERENCES = reactive({
  question: computed(() => `{{${t('workflow.start.label')}.question}}`),
  memory: computed(() => `{{${t('workflow.start.label')}.memory}}`),
})

export const FILE_REFERENCE_EXAMPLE = JSON.stringify(
  [{ name: 'File Name', url: './oss/file/019d8ac3-e2c6-7ff2-8956-c9c98f0e11f4', file_id: '019d8ac3-e2c6-7ff2-8956-c9c98f0e11f4' }],
  null,
  2,
)
