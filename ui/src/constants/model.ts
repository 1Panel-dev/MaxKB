import { computed, reactive } from 'vue'
import { t } from '@/locales'
/** 模型业务和共享控件共用的类型文案；协议值保持不变。 */
export const MODEL_TYPE_LABELS: Record<string, string> = reactive({
  LLM: computed(() => t('model.types.llm.label')),
  EMBEDDING: computed(() => t('model.types.embedding.label')),
  RERANKER: computed(() => t('model.types.reranker.label')),
  STT: computed(() => t('model.types.stt.label')),
  TTS: computed(() => t('model.types.tts.label')),
  IMAGE: computed(() => t('model.types.image.label')),
  TTI: computed(() => t('model.types.tti.label')),
  ITV: computed(() => t('model.types.itv.label')),
  TTV: computed(() => t('model.types.ttv.label')),
})
