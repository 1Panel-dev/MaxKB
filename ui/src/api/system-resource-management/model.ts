import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type {
  ListModelRequest,
  Model,
  CreateModelRequest,
  EditModelRequest,
} from '@/api/type/model'
import type { pageRequest } from '@/api/type/common'
import type { FormField } from '@/components/dynamics-form/type'

const prefix = '/system/resource'

/**
 * 获得模型列表
 * @params 参数 name, model_type, model_name
 */
const getModelListPage: (
  page: pageRequest,
  data?: ListModelRequest,
  loading?: Ref<boolean>,
) => Promise<Result<Array<Model>>> = (page, data, loading) => {
  return get(`${prefix}/model/${page.current_page}/${page.page_size}`, data, loading)
}

/**
 * 获得下拉选择框模型列表
 * @params 参数 name, model_type, model_name
 */
const getSelectModelList: (
  data?: ListModelRequest,
  loading?: Ref<boolean>,
) => Promise<Result<Array<Model>>> = (data, loading) => {
  return get(`${prefix}/model/model_list`, data, loading).then((ok) => {
    return {
      ...ok,
      data: [
        ...ok.data.shared_model.map((m: any) => {
          return { ...m, type: 'share' }
        }),
        ...ok.data.model.map((m: any) => {
          return { ...m, type: 'workspace' }
        }),
      ],
    }
  })
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
  return get(`${prefix}/model/${model_id}/model_params_form`, {}, loading)
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
  return post(`${prefix}/model`, request, {}, loading)
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
  return put(`${prefix}/model/${model_id}`, request, {}, loading)
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
  return put(`${prefix}/model/${model_id}/model_params_form`, request, {}, loading)
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
  return get(`${prefix}/model/${model_id}`, {}, loading)
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
  return get(`${prefix}/model/${model_id}/meta`, {}, loading)
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
  return put(`${prefix}/model/${model_id}/pause_download`, undefined, {}, loading)
}
const deleteModel: (model_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  model_id,
  loading,
) => {
  return del(`${prefix}/model/${model_id}`, undefined, {}, loading)
}
export default {
  getModelListPage,
  createModel,
  updateModel,
  deleteModel,
  getModelById,
  getModelMetaById,
  pauseDownload,
  getModelParamsForm,
  updateModelParamsForm,
  getSelectModelList,
}
