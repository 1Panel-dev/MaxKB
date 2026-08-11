export interface Provider {
  provider: string
  name: string
  icon: string
}

export interface ListModelRequest {
  name?: string
  model_type?: string
  model_name?: string
  provider?: string
  workspace_id?: string
}

export interface Model {
  id: string
  name: string
  model_type: string
  user_id: string
  username: string
  nick_name: string
  model_name: string
  credential: any
  provider: string
  status: 'SUCCESS' | 'DOWNLOAD' | 'ERROR' | 'PAUSE_DOWNLOAD'
  meta: Record<string, any>
  model_params_form: Record<string, any>[]
  resource_count: number
  create_time?: string
  update_time?: string
  workspace_id?: string
}

export interface CreateModelRequest {
  name: string
  model_type: string
  model_name: string
  credential: any
  provider: string
  model_params_form?: any[]
}

export interface EditModelRequest {
  name: string
  model_type: string
  model_name: string
  credential: any
}

export interface BaseModel {
  name: string
  desc: string
  model_type: string
}
