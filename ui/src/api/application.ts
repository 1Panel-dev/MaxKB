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
const postApplication: (data: ApplicationFormType) => Promise<Result<any>> = (data) => {
  return post(`${prefix}`, data)
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
// 对话
/**
 * 创建数据集
 * @param 参数 
 * chat_id: string
 * {
    "message": "string",
  }
 */
const postChatMessage: (chat_id: string, message: string) => Promise<any> = (chat_id, message) => {
  return postStream(`/api/${prefix}/chat_message/${chat_id}`, { message })
}
export default {
  getAllAppilcation,
  getApplication,
  postApplication,
  postChatOpen,
  postChatMessage
}
