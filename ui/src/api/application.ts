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
  return get(`${prefix}/${applicaiton_id}/access_token`, undefined, loading)
}

/**
 * 应用认证
 * @param 参数 
 {
  "access_token": "string"
}
 */
const postAppAuthentication: (access_token: string, loading?: Ref<boolean>) => Promise<any> = (
  access_token,
  loading
) => {
  return post(`${prefix}/authentication`, { access_token }, undefined, loading)
}

/**
 * 对话获取应用相关信息
 * @param 参数 
 {
  "access_token": "string"
}
 */
const getProfile: (loading?: Ref<boolean>) => Promise<any> = (loading) => {
  return get(`${prefix}/profile`, undefined, loading)
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
 * 正式回话Id
 * @param 参数 
 * {
  "model_id": "string",
  "multiple_rounds_dialogue": true,
  "dataset_id_list": [
    "string"
  ]
}
 */
const getChatOpen: (applicaiton_id: String) => Promise<Result<any>> = (applicaiton_id) => {
  return get(`${prefix}/${applicaiton_id}/chat/open`)
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
 * 点赞、点踩
 * @param 参数 
 * application_id : string; chat_id : string; chat_record_id : string
 * {
    "vote_status": "string", // -1 0 1
  }
 */
const putChatVote: (
  application_id: string,
  chat_id: string,
  chat_record_id: string,
  vote_status: string,
  loading?: Ref<boolean>
) => Promise<any> = (application_id, chat_id, chat_record_id, vote_status, loading) => {
  return put(
    `${prefix}/${application_id}/chat/${chat_id}/chat_record/${chat_record_id}/vote`,
    {
      vote_status
    },
    undefined,
    loading
  )
}

export default {
  getAllAppilcation,
  getApplication,
  postApplication,
  putApplication,
  postChatOpen,
  getChatOpen,
  postChatMessage,
  delApplication,
  getApplicationDetail,
  getApplicationDataset,
  getAPIKey,
  getAccessToken,
  postAppAuthentication,
  getProfile,
  putChatVote
}
