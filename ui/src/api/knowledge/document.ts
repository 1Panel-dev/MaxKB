import { Result } from '@/request/Result'
import { del, exportExcel, exportFile, get, post, put } from '@/request/index'
import type { Ref } from 'vue'
import type { KeyValue, pageRequest } from '@/api/type/common'

import useStore from '@/stores'

const prefix: any = {_value: '/workspace/'}
Object.defineProperty(prefix, 'value', {
  get: function () {
    const {user} = useStore()
    return this._value + user.getWorkspaceId() + '/knowledge'
  },
})

/**
 * 文档列表（无分页）
 * @param 参数  knowledge_id,
 * param {
 "   name": "string",
 }
 */

const getDocumentList: (knowledge_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  loading,
) => {
  return get(`${prefix.value}/${knowledge_id}/document`, undefined, loading)
}

/**
 * 文档分页列表
 * @param 参数  knowledge_id,
 * param {
 "name": "string",
 folder_id: "string",
 }
 */

const getDocumentPage: (
  knowledge_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, page, param, loading) => {
  return get(
    `${prefix.value}/${knowledge_id}/document/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 文档详情
 * @param 参数 knowledge_id
 */
const getDocumentDetail: (
  knowledge_id: string,
  document_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, loading) => {
  return get(`${prefix.value}/${knowledge_id}/document/${document_id}`,
    {},
    loading,)
}

/**
 * 修改文档
 * @param 参数
 * knowledge_id, document_id,
 * {
 "name": "string",
 "is_active": true,
 "meta": {}
 }
 */
const putDocument: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, data: any, loading) => {
  return put(`${prefix.value}/${knowledge_id}/document/${document_id}`, data, undefined, loading)
}

/**
 * 删除文档
 * @param 参数 knowledge_id, document_id,
 */
const delDocument: (
  knowledge_id: string,
  document_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, loading) => {
  return del(`${prefix.value}/${knowledge_id}/document/${document_id}`, loading)
}

/**
 * 批量取消文档任务
 * @param 参数 knowledge_id,
 *{
 "id_list": [
 "3fa85f64-5717-4562-b3fc-2c963f66afa6"
 ],
 "type": 0
 }
 */

const putBatchCancelTask: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(`${prefix.value}/${knowledge_id}/document/batch_cancel_task`, data, undefined, loading)
}

/**
 * 取消文档任务
 * @param 参数 knowledge_id, document_id,
 */
const putCancelTask: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, data, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/${document_id}/cancel_task`,
    data,
    undefined,
    loading,
  )
}

/**
 * 下载原文档
 * @param 参数 knowledge_id
 */
const getDownloadSourceFile: (knowledge_id: string, document_id: string, document_name: string) => Promise<Result<any>> = (
  knowledge_id,
  document_id,
  document_name,
) => {
  return exportFile(document_name, `${prefix.value}/${knowledge_id}/document/${document_id}/download_source_file`, {}, undefined)
}

const postReplaceSourceFile: (knowledge_id: string, document_id: string, data: any) => Promise<Result<any>> = (
  knowledge_id,
  document_id,
  data,
) => {
  return post(`${prefix.value}/${knowledge_id}/document/${document_id}/replace_source_file`, data, {}, undefined)
}

/**
 * 导出文档
 * @param document_name 文档名称
 * @param knowledge_id    数据集id
 * @param document_id   文档id
 * @param loading       加载器
 * @returns
 */
const exportDocument: (
  document_name: string,
  knowledge_id: string,
  document_id: string,
  loading?: Ref<boolean>,
) => Promise<any> = (document_name, knowledge_id, document_id, loading) => {
  return exportExcel(
    document_name.trim() + '.xlsx',
    `${prefix.value}/${knowledge_id}/document/${document_id}/export`,
    {},
    loading,
  )
}
/**
 * 导出文档
 * @param document_name 文档名称
 * @param knowledge_id    数据集id
 * @param document_id   文档id
 * @param loading       加载器
 * @returns
 */
const exportDocumentZip: (
  document_name: string,
  knowledge_id: string,
  document_id: string,
  loading?: Ref<boolean>,
) => Promise<any> = (document_name, knowledge_id, document_id, loading) => {
  return exportFile(
    document_name.trim() + '.zip',
    `${prefix.value}/${knowledge_id}/document/${document_id}/export_zip`,
    {},
    loading,
  )
}

/**
 * 刷新文档向量库
 * @param 参数
 * knowledge_id, document_id,
 * {
 "state_list": [
 "string"
 ]
 }
 */
const putDocumentRefresh: (
  knowledge_id: string,
  document_id: string,
  state_list: Array<string>,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, state_list, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/${document_id}/refresh`,
    {state_list},
    undefined,
    loading,
  )
}

/**
 * 同步web站点类型
 * @param 参数
 * knowledge_id, document_id,
 */
const putDocumentSync: (
  knowledge_id: string,
  document_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/${document_id}/sync`,
    undefined,
    undefined,
    loading,
  )
}

/**
 * 创建批量文档
 * @param 参数
 {
 "name": "string",
 "paragraphs": [
 {
 "content": "string",
 "title": "string",
 "problem_list": [
 {
 "id": "string",
 "content": "string"
 }
 ],
 "is_active": true
 }
 ],
 "source_file_id": string
 }
 */
const putMulDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/batch_create`,
    data,
    {},
    loading,
    1000 * 60 * 5,
  )
}

/**
 * 批量删除文档
 * @param 参数 knowledge_id,
 * {
 "id_list": [String]
 }
 */
const delMulDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/batch_delete`,
    {id_list: data},
    undefined,
    loading,
  )
}

/**
 * 批量关联
 * @param 参数 knowledge_id,
 {
 "document_id_list": [
 "string"
 ],
 "model_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
 "prompt": "string",
 "state_list": [
 "string"
 ]
 }
 */
const putBatchGenerateRelated: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/batch_generate_related`,
    data,
    undefined,
    loading,
  )
}

/**
 * 批量修改命中方式
 * @param knowledge_id 知识库id
 * @param data
 * {id_list:[],hit_handling_method:'directly_return|optimization',directly_return_similarity}
 * @param loading
 * @returns
 */
const putBatchEditHitHandling: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/batch_hit_handling`,
    data,
    undefined,
    loading,
  )
}

/**
 * 批量刷新文档向量库
 * @param knowledge_id 知识库id
 * @param data
 {
 "id_list": [
 "string"
 ],
 "state_list": [
 "string"
 ]
 }
 * @param loading
 * @returns
 */
const putBatchRefresh: (
  knowledge_id: string,
  data: any,
  stateList: Array<string>,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, stateList, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/batch_refresh`,
    {id_list: data, state_list: stateList},
    undefined,
    loading,
  )
}

/**
 * 批量同步文档
 * @param 参数 knowledge_id,
 */
const putMulSyncDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/batch_sync`,
    {id_list: data},
    undefined,
    loading,
  )
}

/**
 * 批量迁移文档
 * @param 参数 knowledge_id,target_knowledge_id,

 */
const putMigrateMulDocument: (
  knowledge_id: string,
  target_knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, target_knowledge_id, data, loading) => {
  return put(
    `${prefix.value}/${knowledge_id}/document/migrate/${target_knowledge_id}`,
    data,
    undefined,
    loading,
  )
}

/**
 * 导入QA文档
 * @param 参数
 * file
 }
 */
const postQADocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return post(`${prefix.value}/${knowledge_id}/document/qa`, data, undefined, loading)
}

/**
 * 分段预览（上传文档）
 * @param 参数  file:file,limit:number,patterns:array,with_filter:boolean
 */
const postSplitDocument: (knowledge_id: string, data: any) => Promise<Result<any>> = (
  knowledge_id,
  data,
) => {
  return post(
    `${prefix.value}/${knowledge_id}/document/split`,
    data,
    undefined,
    undefined,
    1000 * 60 * 60,
  )
}

/**
 * 分段标识列表
 * @param loading 加载器
 * @returns 分段标识列表
 */
const listSplitPattern: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<KeyValue<string, string>>>> = (knowledge_id, loading) => {
  return get(`${prefix.value}/${knowledge_id}/document/split_pattern`, {}, loading)
}

/**
 * 导入表格
 * @param 参数
 * file
 */
const postTableDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return post(`${prefix.value}/${knowledge_id}/document/table`, data, undefined, loading)
}

/**
 * 获得QA模版
 * @param 参数 fileName,type,
 */
const exportQATemplate: (fileName: string, type: string, loading?: Ref<boolean>) => void = (
  fileName,
  type,
  loading,
) => {
  return exportExcel(fileName, `/workspace/knowledge/document/template/export`, {type}, loading)
}

/**
 * 获得table模版
 * @param 参数 fileName,type,
 */
const exportTableTemplate: (fileName: string, type: string, loading?: Ref<boolean>) => void = (
  fileName,
  type,
  loading,
) => {
  return exportExcel(
    fileName,
    `/workspace/knowledge/document/table_template/export`,
    {type},
    loading,
  )
}

/**
 * 创建Web站点文档
 * @param 参数
 * {
 "source_url_list": [
 "string"
 ],
 "selector": "string"
 }
 }
 */
const postWebDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return post(`${prefix.value}/${knowledge_id}/document/web`, data, undefined, loading)
}

/**
 * 飞书导入获得相关文档
 * @param 参数
 * {
 "source_url_list": [
 "string"
 ],
 "selector": "string"
 }
 }
 */
const getLarkDocumentList: (
  knowledge_id: string,
  folder_token: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, folder_token, data, loading) => {
  return post(
    `${prefix.value}/lark/${knowledge_id}/${folder_token}/doc_list`,
    data,
    undefined,
    loading,
  )
}

/**
 * 同步飞书文档
 */
const putLarkDocumentSync: (
  knowledge_id: string,
  document_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, loading) => {
  return put(
    `${prefix.value}/lark/${knowledge_id}/document/${document_id}/sync`,
    undefined,
    undefined,
    loading,
  )
}

/**
 * 批量同步飞书文档
 */
const putMulLarkSyncDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(`${prefix.value}/lark/${knowledge_id}/_batch`, {id_list: data}, undefined, loading)
}

/**
 * 导入飞书文档
 */
const importLarkDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, data, loading) => {
  return post(`${prefix.value}/lark/${knowledge_id}/import`, data, null, loading)
}

const getDocumentTags: (
  knowledge_id: string,
  document_id: string,
  params: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<string>>> = (knowledge_id, document_id, params, loading) => {
  return get(`${prefix.value}/${knowledge_id}/document/${document_id}/tags`, params, loading)
}

const postDocumentTags: (
  knowledge_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, data, loading) => {
  return post(`${prefix.value}/${knowledge_id}/document/${document_id}/tags`, data, null, loading)
}

const postMulDocumentTags: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return post(`${prefix.value}/${knowledge_id}/document/batch_add_tag`, data, null, loading)
}

const delMulDocumentTag: (
  knowledge_id: string,
  document_id: string,
  tags: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, document_id, tags, loading) => {
  return put(`${prefix.value}/${knowledge_id}/document/${document_id}/tags/batch_delete`, tags, null, loading)
}

export default {
  getDocumentList,
  getDocumentPage,
  getDocumentDetail,
  putDocument,
  delDocument,
  putBatchCancelTask,
  putCancelTask,
  getDownloadSourceFile,
  postReplaceSourceFile,
  exportDocument,
  exportDocumentZip,
  putDocumentRefresh,
  putDocumentSync,
  putMulDocument,
  delMulDocument,
  putBatchGenerateRelated,
  putBatchEditHitHandling,
  putBatchRefresh,
  putMulSyncDocument,
  putMigrateMulDocument,
  postQADocument,
  postSplitDocument,
  listSplitPattern,
  postTableDocument,
  exportQATemplate,
  exportTableTemplate,
  postWebDocument,
  getLarkDocumentList,
  putLarkDocumentSync,
  putMulLarkSyncDocument,
  importLarkDocument,
  getDocumentTags,
  postDocumentTags,
  postMulDocumentTags,
  delMulDocumentTag
}
