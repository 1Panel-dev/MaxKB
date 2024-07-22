import { store } from '@/stores'
import type { Dict } from './common'
interface modelRequest {
  name: string
  model_type: string
  model_name: string
}

interface Provider {
  /**
   * 供应商代号
   */
  provider: string
  /**
   * 供应商名称
   */
  name: string
  /**
   * 供应商icon
   */
  icon: string
}

interface ListModelRequest {
  /**
   * 模型名称
   */
  name?: string
  /**
   * 模型类型
   */
  model_type?: string
  /**
   * 基础模型名称
   */
  model_name?: string
  /**
   * 供应商
   */
  provider?: string
}

interface Model {
  /**
   * 主键id
   */
  id: string
  /**
   * 模型名
   */
  name: string
  /**
   * 模型类型
   */
  model_type: string
  user_id: string
  permission_type: 'PUBLIC' | 'PRIVATE'
  /**
   * 基础模型
   */
  model_name: string
  /**
   * 认证信息
   */
  credential: any
  /**
   * 供应商
   */
  provider: string
  /**
   * 状态
   */
  status: 'SUCCESS' | 'DOWNLOAD' | 'ERROR' | 'PAUSE_DOWNLOAD'
  /**
   * 元数据
   */
  meta: Dict<any>
}
interface CreateModelRequest {
  /**
   * 模型名
   */
  name: string
  /**
   * 模型类型
   */
  model_type: string
  /**
   * 基础模型
   */
  model_name: string
  /**
   * 认证信息
   */
  credential: any
  /**
   * 供应商
   */
  provider: string
}

interface EditModelRequest {
  /**
   * 模型名
   */
  name: string
  /**
   * 模型类型
   */
  model_type: string
  /**
   * 基础模型
   */
  model_name: string
  /**
   * 认证信息
   */
  credential: any
}

interface BaseModel {
  /**
   * 基础模型名称
   */
  name: string
  /**
   * 基础模型描述
   */
  desc: string
  /**
   * 基础模型类型
   */
  model_type: string
}
export type {
  modelRequest,
  Provider,
  ListModelRequest,
  Model,
  BaseModel,
  CreateModelRequest,
  EditModelRequest
}
