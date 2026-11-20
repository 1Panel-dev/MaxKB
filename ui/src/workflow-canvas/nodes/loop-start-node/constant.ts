import { computed, reactive } from 'vue'
import { t } from '@/locales'

// 循环引擎自带的输出参数（内置，界面上不展示、不可被用户修改）
export const LOOP_BUILTIN_FIELDS = reactive([
  { field: 'index', label: computed(() => t('workflow.loopStart.index')) },
  { field: 'item', label: computed(() => t('workflow.loopStart.item')) },
] as const)

export const isLoopBuiltinField = (value?: string) => !!value && LOOP_BUILTIN_FIELDS.some((item) => item.field === value)
