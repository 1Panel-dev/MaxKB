import { modelType } from '@/enums/model'
export const modelTypeList = [
  { text: modelType['LLM'], value: 'LLM' },
  { text: modelType['EMBEDDING'], value: 'EMBEDDING' },
  { text: modelType['RERANKER'], value: 'RERANKER' },
  { text: modelType['STT'], value: 'STT' },
  { text: modelType['TTS'], value: 'TTS' },
  { text: modelType['IMAGE'], value: 'IMAGE' },
  { text: modelType['TTI'], value: 'TTI' }
]
