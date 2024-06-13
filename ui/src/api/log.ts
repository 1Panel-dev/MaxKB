import { Result } from '@/request/Result'
import { get, del, put, exportExcel } from '@/request/index'
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
  application_id: String,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, page, param, loading) => {
  return get(
    `${prefix}/${application_id}/chat/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

const exportChatLog: (
  application_id: string,
  application_name: string,
  param: any,
  loading?: Ref<boolean>
) => void = (application_id, application_name, param, loading) => {
  exportExcel(application_name, `${prefix}/${application_id}/chat/export`, param, loading)
}

/**
 * 删除日志
 * @param 参数 application_id, chat_id,
 */
const delChatLog: (
  application_id: string,
  chat_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (application_id, chat_id, loading) => {
  return del(`${prefix}/${application_id}/chat/${chat_id}`, undefined, {}, loading)
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
  application_id: String,
  chart_id: String,
  page: pageRequest,
  loading?: Ref<boolean>,
  order_asc?: boolean
) => Promise<Result<any>> = (application_id, chart_id, page, loading, order_asc) => {
  return get(
    `${prefix}/${application_id}/chat/${chart_id}/chat_record/${page.current_page}/${page.page_size}`,
    { order_asc: order_asc !== undefined ? order_asc : true },
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
  application_id: String,
  chart_id: String,
  chart_record_id: String,
  dataset_id: String,
  document_id: String,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (
  application_id,
  chart_id,
  chart_record_id,
  dataset_id,
  document_id,
  data,
  loading
) => {
  return put(
    `${prefix}/${application_id}/chat/${chart_id}/chat_record/${chart_record_id}/dataset/${dataset_id}/document_id/${document_id}/improve`,
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
  application_id: String,
  chart_id: String,
  chart_record_id: String,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, chart_id, chart_record_id, loading) => {
  return get(
    `${prefix}/${application_id}/chat/${chart_id}/chat_record/${chart_record_id}/improve`,
    undefined,
    loading
  )
}

/**
 * 删除标注
 * @param 参数
 * application_id, chart_id,  chart_record_id, dataset_id, document_id,paragraph_id
 */
const delMarkRecord: (
  application_id: String,
  chart_id: String,
  chart_record_id: String,
  dataset_id: String,
  document_id: String,
  paragraph_id: String,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (
  application_id,
  chart_id,
  chart_record_id,
  dataset_id,
  document_id,
  paragraph_id,
  loading
) => {
  return del(
    `${prefix}/${application_id}/chat/${chart_id}/chat_record/${chart_record_id}/dataset/${dataset_id}/document_id/${document_id}/improve/${paragraph_id}`,
    undefined,
    {},
    loading
  )
}

/**
 * 获取对话记录详情
 * @param 参数
 * application_id, chart_id,  chart_record_id
 */
const getRecordDetail: (
  application_id: String,
  chart_id: String,
  chart_record_id: String,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, chart_id, chart_record_id, loading) => {
  return get(
    `${prefix}/${application_id}/chat/${chart_id}/chat_record/${chart_record_id}`,
    undefined,
    loading
  )
}

const getChatLogClient: (
  application_id: String,
  page: pageRequest,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, page, loading) => {
  return get(
    `${prefix}/${application_id}/chat/client/${page.current_page}/${page.page_size}`,
    null,
    loading
  )
}

/**
 * 客户端删除日志
 * @param 参数 application_id, chat_id,
 */
const delChatClientLog: (
  application_id: string,
  chat_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (application_id, chat_id, loading) => {
  return del(`${prefix}/${application_id}/chat/client/${chat_id}`, undefined, {}, loading)
}

export default {
  getChatLog,
  delChatLog,
  getChatRecordLog,
  putChatRecordLog,
  getMarkRecord,
  getRecordDetail,
  delMarkRecord,
  exportChatLog,
  getChatLogClient,
  delChatClientLog
}
