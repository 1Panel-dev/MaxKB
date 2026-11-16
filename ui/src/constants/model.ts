/** 模型类型的翻译键，使用处通过 t() 获取显示文案。 */
export const MODEL_TYPE_LABELS: Record<string, string> = {
  LLM: 'model.types.llm.label',
  EMBEDDING: 'model.types.embedding.label',
  RERANKER: 'model.types.reranker.label',
  STT: 'model.types.speechToText.label',
  TTS: 'model.types.textToSpeech.label',
  IMAGE: 'model.types.vision.label',
  TTI: 'model.types.imageGeneration.label',
  ITV: 'model.types.imageToVideo.label',
  TTV: 'model.types.textToVideo.label',
}
