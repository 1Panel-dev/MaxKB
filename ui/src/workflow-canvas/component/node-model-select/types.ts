export type NodeModelSource = 'default' | 'custom' | 'reference'

export interface NodeModelData {
  model_id_type?: NodeModelSource
  model_id?: string
  model_id_reference?: string[]
  stt_model_id_type?: NodeModelSource
  stt_model_id?: string
  stt_model_id_reference?: string[]
  tts_model_id_type?: NodeModelSource
  tts_model_id?: string
  tts_model_id_reference?: string[]
  model_params_setting: Record<string, unknown>
}

// 映射仅支持现有节点协议，同一组来源、模型和引用字段保持对应。
export type NodeModelFields = {
  [Prefix in '' | 'stt_' | 'tts_']: {
    source: `${Prefix}model_id_type`
    id: `${Prefix}model_id`
    reference: `${Prefix}model_id_reference`
    params: 'model_params_setting'
  }
}['' | 'stt_' | 'tts_']
