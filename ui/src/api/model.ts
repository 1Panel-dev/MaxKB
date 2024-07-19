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
 * 获得模型列表
 * @params 参数 name, model_type, model_name
 */
const getModel: (
  request?: ListModelRequest,
  loading?: Ref<boolean>
) => Promise<Result<Array<Model>>> = (data, loading) => {
  return get(`${prefix}`, data, loading)
}

/**
 * 获得供应商列表
 */
const getProvider: (loading?: Ref<boolean>) => Promise<Result<Array<Provider>>> = (loading) => {
  return get(`${prefix_provider}`, {}, loading)
}

/**
 * 获取模型创建表单
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
 * 获取模型类型列表
 * @param provider 供应商
 * @param loading  加载器
 * @returns 模型类型列表
 */
const listModelType: (
  provider: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<KeyValue<string, string>>>> = (provider, loading?: Ref<boolean>) => {
  return get(`${prefix_provider}/model_type_list`, { provider }, loading)
}

/**
 * 获取基础模型列表
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
 * 创建模型
 * @param request 请求对象
 * @param loading 加载器
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
 * 获取模型详情根据模型id 包括认证信息
 * @param model_id 模型id
 * @param loading  加载器
 * @returns
 */
const getModelById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading
) => {
  return get(`${prefix}/${model_id}`, {}, loading)
}
/**
 * 获取模型信息不包括认证信息根据模型id
 * @param model_id 模型id
 * @param loading  加载器
 * @returns
 */
const getModelMetaById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading
) => {
  return get(`${prefix}/${model_id}/meta`, {}, loading)
}
/**
 * 暂停下载
 * @param model_id 模型id
 * @param loading 加载器
 * @returns
 */
const pauseDownload: (model_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  model_id,
  loading
) => {
  return put(`${prefix}/${model_id}/pause_download`, undefined, {}, loading)
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
  getModelMetaById,
  pauseDownload
}
