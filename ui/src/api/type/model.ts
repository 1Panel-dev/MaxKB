import { store } from '@/stores'
import type { Dict } from './common'
interface modelRequest {
  name: string
  model_type: string
  model_name: string
}

interface Provider {
  /**
   * 供應商代號
   */
  provider: string
  /**
   * 供應商名稱
   */
  name: string
  /**
   * 供應商icon
   */
  icon: string
}

interface ListModelRequest {
  /**
   * 模型名稱
   */
  name?: string
  /**
   * 模型類型
   */
  model_type?: string
  /**
   * 基礎模型名稱
   */
  model_name?: string
  /**
   * 供應商
   */
  provider?: string
}

interface Model {
  /**
   * 主鍵id
   */
  id: string
  /**
   * 模型名
   */
  name: string
  /**
   * 模型類型
   */
  model_type: string
  /**
   * 基礎模型
   */
  model_name: string
  /**
   * 認證信息
   */
  credential: any
  /**
   * 供應商
   */
  provider: string
  /**
   * 狀態
   */
  status: 'SUCCESS' | 'DOWNLOAD' | 'ERROR'
  /**
   * 元數據
   */
  meta: Dict<any>
}
interface CreateModelRequest {
  /**
   * 模型名
   */
  name: string
  /**
   * 模型類型
   */
  model_type: string
  /**
   * 基礎模型
   */
  model_name: string
  /**
   * 認證信息
   */
  credential: any
  /**
   * 供應商
   */
  provider: string
}

interface EditModelRequest {
  /**
   * 模型名
   */
  name: string
  /**
   * 模型類型
   */
  model_type: string
  /**
   * 基礎模型
   */
  model_name: string
  /**
   * 認證信息
   */
  credential: any
}

interface BaseModel {
  /**
   * 基礎模型名稱
   */
  name: string
  /**
   * 基礎模型描述
   */
  desc: string
  /**
   * 基礎模型類型
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
