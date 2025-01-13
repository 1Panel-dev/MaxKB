import { modelType } from '@/enums/model'
import { t } from '@/locales'
export const modelTypeList = [
  { text: t(modelType['LLM']), value: 'LLM' },
  { text: t(modelType['EMBEDDING']), value: 'EMBEDDING' },
  { text: t(modelType['RERANKER']), value: 'RERANKER' },
  { text: t(modelType['STT']), value: 'STT' },
  { text: t(modelType['TTS']), value: 'TTS' },
  { text: t(modelType['IMAGE']), value: 'IMAGE' },
  { text: t(modelType['TTI']), value: 'TTI' }
]
