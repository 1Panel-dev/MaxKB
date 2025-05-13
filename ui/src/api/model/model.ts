import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type {
  ListModelRequest,
  Model,
  CreateModelRequest,
  EditModelRequest,
} from '@/api/type/model'
import type { FormField } from '@/components/dynamics-form/type'

const prefix = '/workspace'

/**
 * 获得模型列表
 * @params 参数 name, model_type, model_name
 */
const getModel: (
  wordspace_id: string,
  request?: ListModelRequest,
  loading?: Ref<boolean>,
) => Promise<Result<Array<Model>>> = (wordspace_id, data, loading) => {
  return get(`${prefix}/${wordspace_id}/model`, data, loading)
}

/**
 * 获取模型参数表单
 * @param model_id 模型id
 * @param loading
 * @returns
 */
const getModelParamsForm: (
  wordspace_id: string,
  model_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<FormField>>> = (wordspace_id, model_id, loading) => {
  return get(`${prefix}/${wordspace_id}/model/${model_id}/model_params_form`, {}, loading)
}

/**
 * 创建模型
 * @param request 请求对象
 * @param loading 加载器
 * @returns
 */
const createModel: (
  wordspace_id: string,
  request: CreateModelRequest,
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (wordspace_id, request, loading) => {
  return post(`${prefix}/${wordspace_id}/model`, request, {}, loading)
}

/**
 * 修改模型
 * @param request 請求對象
 * @param loading 加載器
 * @returns
 */
const updateModel: (
  wordspace_id: string,
  model_id: string,
  request: EditModelRequest,
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (wordspace_id, model_id, request, loading) => {
  return put(`${prefix}/${wordspace_id}/model/${model_id}`, request, {}, loading)
}

/**
 * 修改模型参数配置
 * @param request 請求對象
 * @param loading 加載器
 * @returns
 */
const updateModelParamsForm: (
  wordspace_id: string,
  model_id: string,
  request: any[],
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (wordspace_id, model_id, request, loading) => {
  return put(`${prefix}/${wordspace_id}/model/${model_id}/model_params_form`, request, {}, loading)
}

/**
 * 获取模型详情根据模型id 包括认证信息
 * @param model_id 模型id
 * @param loading  加载器
 * @returns
 */
const getModelById: (
  wordspace_id: string,
  model_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (wordspace_id, model_id, loading) => {
  return get(`${prefix}/${wordspace_id}/model/${model_id}`, {}, loading)
}
/**
 * 获取模型信息不包括认证信息根据模型id
 * @param model_id 模型id
 * @param loading  加载器
 * @returns
 */
const getModelMetaById: (
  wordspace_id: string,
  model_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (wordspace_id, model_id, loading) => {
  return get(`${prefix}/${wordspace_id}/model/${model_id}/meta`, {}, loading)
}
/**
 * 暂停下载
 * @param model_id 模型id
 * @param loading 加载器
 * @returns
 */
const pauseDownload: (
  wordspace_id: string,
  model_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (wordspace_id, model_id, loading) => {
  return put(`${prefix}/${wordspace_id}/model/${model_id}/pause_download`, undefined, {}, loading)
}
const deleteModel: (
  wordspace_id: string,
  model_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (wordspace_id, model_id, loading) => {
  return del(`${prefix}/${wordspace_id}/model/${model_id}`, undefined, {}, loading)
}
export default {
  getModel,
  createModel,
  updateModel,
  deleteModel,
  getModelById,
  getModelMetaById,
  pauseDownload,
  getModelParamsForm,
  updateModelParamsForm,
}
