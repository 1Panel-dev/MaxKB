import { Result } from '@/request/Result'
import { get, post, postStream, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/application'
/**
 * 对话日志
 * @param 参数 
 * application_id, history_day
 * page  {
              "current_page": "string",
              "page_size": "string",
            }
* param  {
              "history_day": "string",
              "search": "string",
            }
 */
const getChatLog: (
  applicaiton_id: String,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (applicaiton_id, page, param, loading) => {
  return get(
    `${prefix}/${applicaiton_id}/chat/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

/**
 * 删除日志
 * @param 参数 applicaiton_id, chat_id,
 */
const delChatLog: (
  applicaiton_id: string,
  chat_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (applicaiton_id, chat_id, loading) => {
  return del(`${prefix}/${applicaiton_id}/chat/${chat_id}`, undefined, {}, loading)
}

/**
 * 日志记录
 * @param 参数
 * application_id, chart_id
 * page {
          "current_page": "string",
          "page_size": "string",
        }
 */
const getChatRecordLog: (
  applicaiton_id: String,
  chart_id: String,
  page: pageRequest,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (applicaiton_id, chart_id, page, loading) => {
  return get(
    `${prefix}/${applicaiton_id}/chat/${chart_id}/chat_record/${page.current_page}/${page.page_size}`,
    undefined,
    loading
  )
}

/**
 * 修改日志内容
 * @param 参数
 * application_id, chart_id,  chart_record_id, dataset_id, document_id
 * data {
          "title": "string",
          "content": "string",
        }
 */
const putChatRecordLog: (
  applicaiton_id: String,
  chart_id: String,
  chart_record_id: String,
  dataset_id: String,
  document_id: String,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (
  applicaiton_id,
  chart_id,
  chart_record_id,
  dataset_id,
  document_id,
  data,
  loading
) => {
  return put(
    `${prefix}/${applicaiton_id}/chat/${chart_id}/chat_record/${chart_record_id}/dataset/${dataset_id}/document_id/${document_id}/improve`,
    data,
    undefined,
    loading
  )
}

/**
 * 获取标注段落列表信息
 * @param 参数
 * application_id, chart_id,  chart_record_id
 */
const getMarkRecord: (
  applicaiton_id: String,
  chart_id: String,
  chart_record_id: String,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (applicaiton_id, chart_id, chart_record_id, loading) => {
  return get(
    `${prefix}/${applicaiton_id}/chat/${chart_id}/chat_record/${chart_record_id}/improve`,
    undefined,
    loading
  )
}

export default {
  getChatLog,
  delChatLog,
  getChatRecordLog,
  putChatRecordLog,
  getMarkRecord
}
