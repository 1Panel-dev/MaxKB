import { Result } from '@/request/Result'
import { get, post, postStream, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'

const prefix = '/application'

/**
 * 获取全部应用
 * @param 参数
 */
const getAllAppilcation: () => Promise<Result<any[]>> = () => {
  return get(`${prefix}`)
}

/**
 * 获取分页应用
 * @param 参数  {
              "current_page": "string",
              "page_size": "string",
              "name": "string",
            }
 */
const getApplication: (param: pageRequest) => Promise<Result<any>> = (param) => {
  return get(
    `${prefix}/${param.current_page}/${param.page_size}`,
    param.name && { name: param.name }
  )
}

/**
 * 获得临时回话Id
 * @param 参数 
 * {
  "model_id": "string",
  "multiple_rounds_dialogue": true,
  "dataset_id_list": [
    "string"
  ]
}
 */
const postChatOpen: (data: ApplicationFormType) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/chat/open`, data)
}
/**
 * 对话
 * @param 参数 
 * chat_id: string
 * {
    "message": "string",
  }
 */
const postChatMessage: (chat_id: string, message: string) => Promise<any> = (chat_id, message) => {
  return postStream(`/api/${prefix}/chat_message/${chat_id}`, { message })
}

/**
 * 创建应用
 * @param 参数 
 * {
  "name": "string",
  "desc": "string",
  "model_id": "string",
  "multiple_rounds_dialogue": true,
  "prologue": "string",
  "example": [
    "string"
  ],
  "dataset_id_list": [
    "string"
  ]
}
 */
const postApplication: (
  data: ApplicationFormType,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 修改应用
 * @param 参数 
 * {
  "name": "string",
  "desc": "string",
  "model_id": "string",
  "multiple_rounds_dialogue": true,
  "prologue": "string",
  "example": [
    "string"
  ],
  "dataset_id_list": [
    "string"
  ]
}
 */
const putApplication: (
  applicaiton_id: String,
  data: ApplicationFormType,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (applicaiton_id, data, loading) => {
  return put(`${prefix}/${applicaiton_id}`, data, undefined, loading)
}

/**
 * 删除应用
 * @param 参数 applicaiton_id
 */
const delApplication: (applicaiton_id: String) => Promise<Result<boolean>> = (applicaiton_id) => {
  return del(`${prefix}/${applicaiton_id}`)
}

/**
 * 应用详情
 * @param 参数 applicaiton_id
 */
const getApplicationDetail: (
  applicaiton_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (applicaiton_id, loading) => {
  return get(`${prefix}/${applicaiton_id}`, undefined, loading)
}

/**
 * 获得当前应用可使用的数据集
 * @param 参数 applicaiton_id
 */
const getApplicationDataset: (
  applicaiton_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (applicaiton_id, loading) => {
  return get(`${prefix}/${applicaiton_id}/list_dataset`, undefined, loading)
}

/**
 * API_KEY列表
 * @param 参数 applicaiton_id
 */
const getAPIKey: (applicaiton_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  applicaiton_id,
  loading
) => {
  return get(`${prefix}/${applicaiton_id}/api_key`, undefined, loading)
}

/**
 * 获取AccessToken
 * @param 参数 applicaiton_id
 */
const getAccessToken: (applicaiton_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  applicaiton_id,
  loading
) => {
  return get(`${prefix}/${applicaiton_id}/access-token`, undefined, loading)
}

export default {
  getAllAppilcation,
  getApplication,
  postApplication,
  putApplication,
  postChatOpen,
  postChatMessage,
  delApplication,
  getApplicationDetail,
  getApplicationDataset,
  getAPIKey,
  getAccessToken
}
