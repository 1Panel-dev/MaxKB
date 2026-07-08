import {Result} from '@/request/Result'
import {
  get,
  post,
  exportExcelPost,
  del,
  put,
} from '@/request/index'
import type {pageRequest} from '@/api/type/common'
import {type Ref} from 'vue'
import useStore from '@/stores'

const prefix: any = {_value: '/workspace/'}
Object.defineProperty(prefix, 'value', {
  get: function () {
    const {user} = useStore()
    return this._value + user.getWorkspaceId() + '/application'
  },
})
/**
 * 对话记录提交至知识库
 * @param data
 * @param loading
 * @param application_id
 * @param knowledge_id
 */

const postChatLogAddKnowledge: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return post(`${prefix.value}/${application_id}/add_knowledge`, data, undefined, loading)
}

/**
 * 对话日志
 * @param 参数
 * application_id
 * param  {
 "start_time": "string",
 "end_time": "string",
 }
 */
const getChatLog: (
  application_id: String,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, page, param, loading) => {
  return get(
    `${prefix.value}/${application_id}/chat/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 获得对话日志记录
 * @param 参数
 * application_id, chart_id,order_asc
 */
const getChatRecordLog: (
  application_id: String,
  chart_id: String,
  page: pageRequest,
  loading?: Ref<boolean>,
  order_asc?: boolean,
) => Promise<Result<any>> = (application_id, chart_id, page, loading, order_asc) => {
  return get(
    `${prefix.value}/${application_id}/chat/${chart_id}/chat_record/${page.current_page}/${page.page_size}`,
    {order_asc: order_asc !== undefined ? order_asc : true},
    loading,
  )
}

/**
 * 获取标注段落列表信息
 * @param 参数
 * application_id, chart_id,  chart_record_id
 */
const getMarkChatRecord: (
  application_id: string,
  chart_id: string,
  chart_record_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (
  application_id,
  chart_id,
  chart_record_id,
  loading,
) => {
  return get(
    `${prefix.value}/${application_id}/chat/${chart_id}/chat_record/${chart_record_id}/improve`,
    undefined,
    loading,
  )
}

/**
 * 修改日志记录内容
 * @param 参数
 * application_id, chart_id,  chart_record_id, knowledge_id, document_id
 * data {
 "title": "string",
 "content": "string",
 "problem_text": "string"
 }
 */
const putChatRecordLog: (
  application_id: String,
  chart_id: String,
  chart_record_id: String,
  knowledge_id: String,
  document_id: String,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (
  application_id,
  chart_id,
  chart_record_id,
  knowledge_id,
  document_id,
  data,
  loading,
) => {
  return put(
    `${prefix.value}/${application_id}/chat/${chart_id}/chat_record/${chart_record_id}/knowledge/${knowledge_id}/document/${document_id}/improve`,
    data,
    undefined,
    loading,
  )
}

/**
 * 删除标注
 * @param 参数
 * application_id, chart_id,  chart_record_id, knowledge_id, document_id,paragraph_id
 */
const delMarkChatRecord: (
  application_id: String,
  chart_id: String,
  chart_record_id: String,
  knowledge_id: String,
  document_id: String,
  paragraph_id: String,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (
  application_id,
  chart_id,
  chart_record_id,
  knowledge_id,
  document_id,
  paragraph_id,
  loading,
) => {
  return del(
    `${prefix.value}/${application_id}/chat/${chart_id}/chat_record/${chart_record_id}/knowledge/${knowledge_id}/document/${document_id}/paragraph/${paragraph_id}/improve`,
    undefined,
    {},
    loading,
  )
}

/**
 * 导出对话日志
 * @param 参数
 * application_id
 * param  {
 "start_time": "string",
 "end_time": "string",
 }
 */
const postExportChatLog: (
  application_id: string,
  application_name: string,
  param: any,
  data: any,
  loading?: Ref<boolean>,
) => void = (application_id, application_name, param, data, loading) => {
  exportExcelPost(
    application_name + '.xlsx',
    `${prefix.value}/${application_id}/chat/export`,
    param,
    data,
    loading,
  )
}
const getChatRecordDetails: (
  application_id: string,
  chat_id: string,
  chat_record_id: string,
  loading?: Ref<boolean>,
) => Promise<any> = (application_id, chat_id, chat_record_id, loading) => {
  return get(
    `${prefix.value}/${application_id}/chat/${chat_id}/chat_record/${chat_record_id}`,
    {},
    loading,
  )
}
export default {
  postChatLogAddKnowledge,
  getChatLog,
  getChatRecordLog,
  getMarkChatRecord,
  putChatRecordLog,
  delMarkChatRecord,
  postExportChatLog,
  getChatRecordDetails,
}
