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
 * page {
          "current_page": "string",
          "page_size": "string",
        }
 * param {
          "name": "string",
        }
 */
const getApplication: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 创建应用
 * @param 参数
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
 */
const putApplication: (
  application_id: String,
  data: ApplicationFormType,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}`, data, undefined, loading)
}

/**
 * 删除应用
 * @param 参数 application_id
 */
const delApplication: (
  application_id: String,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (application_id, loading) => {
  return del(`${prefix}/${application_id}`, undefined, {}, loading)
}

/**
 * 应用详情
 * @param 参数 application_id
 */
const getApplicationDetail: (
  application_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}`, undefined, loading)
}

/**
 * 获得当前应用可使用的知识库
 * @param 参数 application_id
 */
const getApplicationDataset: (
  application_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}/list_dataset`, undefined, loading)
}

/**
 * 获取AccessToken
 * @param 参数 application_id
 */
const getAccessToken: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading
) => {
  return get(`${prefix}/${application_id}/access_token`, undefined, loading)
}

/**
 * 修改AccessToken
 * @param 参数 application_id
 * data {
 *  "is_active": true
 * }
 */
const putAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/access_token`, data, undefined, loading)
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
const getAppProfile: (loading?: Ref<boolean>) => Promise<any> = (loading) => {
  return get(`${prefix}/profile`, undefined, loading)
}

/**
 * 获得临时回话Id
 * @param 参数 

}
 */
const postChatOpen: (data: ApplicationFormType) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/chat/open`, data)
}

/**
 * 获得工作流临时回话Id
 * @param 参数 

}
 */
const postWorkflowChatOpen: (data: ApplicationFormType) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/chat_workflow/open`, data)
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
const getChatOpen: (application_id: String) => Promise<Result<any>> = (application_id) => {
  return get(`${prefix}/${application_id}/chat/open`)
}
/**
 * 对话
 * @param 参数
 * chat_id: string
 * data
 */
const postChatMessage: (chat_id: string, data: any) => Promise<any> = (chat_id, data) => {
  return postStream(`/api${prefix}/chat_message/${chat_id}`, data)
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

/**
 * 命中测试列表
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getApplicationHitTest: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (application_id, data, loading) => {
  return get(`${prefix}/${application_id}/hit_test`, data, loading)
}

/**
 * 获取当前用户可使用的模型列表
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getApplicationModel: (
  application_id: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}/model`, loading)
}

/**
 * 发布应用
 * @param 参数
 */
const putPublishApplication: (
  application_id: String,
  data: ApplicationFormType,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/publish`, data, undefined, loading)
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
  getAccessToken,
  putAccessToken,
  postAppAuthentication,
  getAppProfile,
  putChatVote,
  getApplicationHitTest,
  getApplicationModel,
  putPublishApplication,
  postWorkflowChatOpen
}
