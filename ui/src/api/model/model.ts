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

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/model'
  },
})

/**
 * 获得模型列表
 * @params 参数 name, model_type, model_name
 */
const getModel: (
  data?: ListModelRequest,
  loading?: Ref<boolean>,
) => Promise<Result<Array<Model>>> = (data, loading) => {
  return get(`${prefix.value}`, data, loading)
}
/**
 * 获取工作空间下重排模型列表
 * @param loading 加载器
 * @returns 重排模型列表
 */
const getRerankerModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix.value}`, { model_type: 'RERANKER' }, loading)
}

/**
 * 获取语音转文本模型列表
 * @param loading
 * @returns 语音转文本模型列表
 */
const getSTTModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix.value}`, { model_type: 'STT' }, loading)
}

/**
 * 获取文本转语音模型列表
 * @param loading
 * @returns
 */
const getTTSModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix.value}`, { model_type: 'TTS' }, loading)
}
/**
 * 获取图片理解模型列表
 * @param loading
 * @returns 图片理解模型列表
 */
const getImageModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix.value}`, { model_type: 'IMAGE' }, loading)
}
/**
 * 获取图片生成模型列表
 * @param loading
 * @returns  图片生成模型列表
 */
const getTTIModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix.value}`, { model_type: 'TTI' }, loading)
}
/**
 * 获取大语言模型列表
 * @param loading
 * @returns 大语言模型列表
 */
const getLLMModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix.value}`, { model_type: 'LLM' }, loading)
}
/**
 * 获取模型参数表单
 * @param model_id 模型id
 * @param loading
 * @returns
 */
const getModelParamsForm: (
  model_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<FormField>>> = (model_id, loading) => {
  return get(`${prefix.value}/${model_id}/model_params_form`, {}, loading)
}

/**
 * 创建模型
 * @param request 请求对象
 * @param loading 加载器
 * @returns
 */
const createModel: (
  request: CreateModelRequest,
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (request, loading) => {
  return post(`${prefix.value}`, request, {}, loading)
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
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (model_id, request, loading) => {
  return put(`${prefix.value}/${model_id}`, request, {}, loading)
}

/**
 * 修改模型参数配置
 * @param request 請求對象
 * @param loading 加載器
 * @returns
 */
const updateModelParamsForm: (
  model_id: string,
  request: any[],
  loading?: Ref<boolean>,
) => Promise<Result<Model>> = (model_id, request, loading) => {
  return put(`${prefix.value}/${model_id}/model_params_form`, request, {}, loading)
}

/**
 * 获取模型详情根据模型id 包括认证信息
 * @param model_id 模型id
 * @param loading  加载器
 * @returns
 */
const getModelById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading,
) => {
  return get(`${prefix.value}/${model_id}`, {}, loading)
}
/**
 * 获取模型信息不包括认证信息根据模型id
 * @param model_id 模型id
 * @param loading  加载器
 * @returns
 */
const getModelMetaById: (model_id: string, loading?: Ref<boolean>) => Promise<Result<Model>> = (
  model_id,
  loading,
) => {
  return get(`${prefix.value}/${model_id}/meta`, {}, loading)
}
/**
 * 暂停下载
 * @param model_id 模型id
 * @param loading 加载器
 * @returns
 */
const pauseDownload: (model_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  model_id,
  loading,
) => {
  return put(`${prefix.value}/${model_id}/pause_download`, undefined, {}, loading)
}
const deleteModel: (model_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  model_id,
  loading,
) => {
  return del(`${prefix.value}/${model_id}`, undefined, {}, loading)
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
  getRerankerModel,
  getSTTModel,
  getTTSModel,
  getImageModel,
  getTTIModel,
  getLLMModel,
}
