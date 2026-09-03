import type { FormField } from '@/components/mk-dynamics-form'

export interface ApiInputField {
  assignment_method: 'api_input'
  default_value: string
  desc: string
  is_required: boolean
  type: 'input'
  variable: string
}

export interface ChatInputField {
  field: string
  label: string
}

export interface FileUploadSetting {
  audio: boolean
  document: boolean
  fileLimit: number
  image: boolean
  local_upload: boolean
  maxFiles: number
  other: boolean
  otherExtensions: string[]
  url_upload: boolean
  video: boolean
}

export interface LongTermSetting {
  long_term_model_id: string
  long_term_model_id_type: 'custom' | 'default'
  long_term_model_params_setting: Record<string, unknown>
  long_term_trigger_setting: Record<string, unknown>
  long_term_trigger_type: 'ROUND' | 'SCHEDULED'
}

export interface BaseNodeForm extends LongTermSetting {
  desc: string
  file_upload_enable: boolean
  file_upload_setting: FileUploadSetting
  long_term_enable: boolean
  name: string
  prologue: string
  stt_autosend: boolean
  stt_model_enable: boolean
  stt_model_id: string
  stt_model_id_type: 'custom' | 'default'
  tts_autoplay: boolean
  tts_model_enable: boolean
  tts_model_id: string
  tts_model_params_setting: Record<string, unknown>
  tts_type: 'BROWSER' | 'CUSTOM' | 'DEFAULT'
}

export type UserInputField = FormField

export const defaultFileUploadSetting: FileUploadSetting = {
  audio: false,
  document: true,
  fileLimit: 50,
  image: false,
  local_upload: true,
  maxFiles: 3,
  other: false,
  otherExtensions: ['PPT', 'DOC'],
  url_upload: false,
  video: false,
}
