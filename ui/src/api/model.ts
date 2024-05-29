import { request } from './../request/index'
import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type {
  modelRequest,
  Provider,
  ListModelRequest,
  Model,
  BaseModel,
  CreateModelRequest,
  EditModelRequest
} from '@/api/type/model'
import type { FormField } from '@/components/dynamics-form/type'
import type { KeyValue } from './type/common'
const prefix = '/model'
const prefix_provider = '/provider'

/**
 * 獲得模型列表
 * @params 參數 name, model_type, model_name
 */
const getModel: (
  request?: ListModelRequest,
  loading?: Ref<boolean>
) => Promise<Result<Array<Model>>> = (data, loading) => {
  return get(`${prefix}`, data, loading)
}

/**
 * 獲得供應商列表
 */
const getProvider: (loading?: Ref<boolean>) => Promise<Result<Array<Provider>>> = (loading) => {
  return get(`${prefix_provider}`, {}, loading)
}

/**
 * 獲取模型創建表單
 * @param provider
 * @param model_type
 * @param model_name
 * @param loading
 * @returns
 */
const getModelCreateForm: (
  provider: string,
  model_type: string,
  model_name: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<FormField>>> = (provider, model_type, model_name, loading) => {
  return get(`${prefix_provider}/model_form`, { provider, model_type, model_name }, loading)
}

/**
 * 獲取模型類型列表
 * @param provider 供應商
 * @param loading  加載器
 * @returns 模型類型列表
 */
const listModelType: (
  provider: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<KeyValue<string, string>>>> = (provider, loading?: Ref<boolean>) => {
  return get(`${prefix_provider}/model_type_list`, { provider }, loading)
}

/**
 * 獲取基礎模型列表
 * @param provider
 * @param model_type
 * @param loading
 * @returns
 */
const listBaseModel: (
  provider: string,
  model_type: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<BaseModel>>> = (provider, model_type, loading) => {
  return get(`${prefix_provider}/model_list`, { provider, model_type }, loading)
}

/**
 * 創建模型
 * @param request 請求對象
 * @param loading 加載器
 * @returns
 */
const createModel: (
  request: CreateModelRequest,
  loading?: Ref<boolean>
) => Promise<Result<Model>> = (request, loading) => {
  return post(`${prefix}`, request, {}, loading)
}

/**
 * 修改模型
 * @param request 請求對象
 * @param loading 加載器
 * @returns
 */
const updateModel: (
  model_id: string,
  request: EditModelRequest,
  loading?: Ref<boolean>
) => Promise<Result<Model>> = (model_id, request, loading) => {
  return put(`${prefix}/${model_id}`, request, {}, loading)
}

/**
 * 獲取模型詳情根據模型id 包括認證信息
 * @param model_id 模型id
 * @param loading  加載器
 * @returns
 */
const getModelById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading
) => {
  return get(`${prefix}/${model_id}`, {}, loading)
}
/**
 * 獲取模型信息不包括認證信息根據模型id
 * @param model_id 模型id
 * @param loading  加載器
 * @returns
 */
const getModelMetaById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading
) => {
  return get(`${prefix}/${model_id}/meta`, {}, loading)
}

const deleteModel: (model_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  model_id,
  loading
) => {
  return del(`${prefix}/${model_id}`, undefined, {}, loading)
}
export default {
  getModel,
  getProvider,
  getModelCreateForm,
  listModelType,
  listBaseModel,
  createModel,
  updateModel,
  deleteModel,
  getModelById,
  getModelMetaById
}
