import { Result } from '@/request/Result'
import { get, post, del, put, exportExcel } from '@/request/index'
import type { Ref } from 'vue'
import type { KeyValue } from '@/api/type/common'
import type { pageRequest } from '@/api/type/common'
const prefix = '/dataset'

/**
 * 分段預覽（上傳文檔）
 * @param 參數  file:file,limit:number,patterns:array,with_filter:boolean
 */
const postSplitDocument: (data: any) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/document/split`, data, undefined, undefined, 1000 * 60 * 60)
}

/**
 * 分段標識列表
 * @param loading 加載器
 * @returns 分段標識列表
 */
const listSplitPattern: (
  loading?: Ref<boolean>
) => Promise<Result<Array<KeyValue<string, string>>>> = (loading) => {
  return get(`${prefix}/document/split_pattern`, {}, loading)
}

/**
 * 文檔分頁列表
 * @param 參數  dataset_id,   
 * page {
              "current_page": "string",
              "page_size": "string",
            }
* param {
          "name": "string",
        }
 */

const getDocument: (
  dataset_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, page, param, loading) => {
  return get(
    `${prefix}/${dataset_id}/document/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

const getAllDocument: (dataset_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  dataset_id,
  loading
) => {
  return get(`${prefix}/${dataset_id}/document`, undefined, loading)
}

/**
 * 創建批量文檔
 * @param 參數 
 * {
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
      ]
    }
  ]
}
 */
const postDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/document/_bach`, data, {}, loading, 1000 * 60 * 5)
}

/**
 * 修改文檔
 * @param 參數 
 * dataset_id, document_id, 
 * {
      "name": "string",
      "is_active": true,
      "meta": {}
    }
 */
const putDocument: (
  dataset_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, data: any, loading) => {
  return put(`${prefix}/${dataset_id}/document/${document_id}`, data, undefined, loading)
}

/**
 * 刪除文檔
 * @param 參數 dataset_id, document_id,
 */
const delDocument: (
  dataset_id: string,
  document_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, document_id, loading) => {
  return del(`${prefix}/${dataset_id}/document/${document_id}`, loading)
}
/**
 * 批量刪除文檔
 * @param 參數 dataset_id,
 */
const delMulDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return del(`${prefix}/${dataset_id}/document/_bach`, undefined, { id_list: data }, loading)
}
/**
 * 文檔詳情
 * @param 參數 dataset_id
 */
const getDocumentDetail: (dataset_id: string, document_id: string) => Promise<Result<any>> = (
  dataset_id,
  document_id
) => {
  return get(`${prefix}/${dataset_id}/document/${document_id}`)
}

/**
 * 刷新文檔向量庫
 * @param 參數
 * dataset_id, document_id,
 */
const putDocumentRefresh: (
  dataset_id: string,
  document_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, loading) => {
  return put(
    `${prefix}/${dataset_id}/document/${document_id}/refresh`,
    undefined,
    undefined,
    loading
  )
}

/**
 * 同步web站點類型
 * @param 參數
 * dataset_id, document_id,
 */
const putDocumentSync: (
  dataset_id: string,
  document_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, loading) => {
  return put(`${prefix}/${dataset_id}/document/${document_id}/sync`, undefined, undefined, loading)
}

/**
 * 批量同步文檔
 * @param 參數 dataset_id,
 */
const delMulSyncDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}/document/_bach`, { id_list: data }, undefined, loading)
}

/**
 * 創建Web站點文檔
 * @param 參數 
 * {
    "source_url_list": [
    "string"
  ],
  "selector": "string"
 }
}
 */
const postWebDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/document/web`, data, undefined, loading)
}

/**
 * 導入QA文檔
 * @param 參數 
 * file
}
 */
const postQADocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/document/qa`, data, undefined, loading)
}

/**
 * 批量遷移文檔
 * @param 參數 dataset_id,target_dataset_id,
 */
const putMigrateMulDocument: (
  dataset_id: string,
  target_dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, target_dataset_id, data, loading) => {
  return put(
    `${prefix}/${dataset_id}/document/migrate/${target_dataset_id}`,
    data,
    undefined,
    loading
  )
}

/**
 * 批量修改命中方式
 * @param dataset_id 知識庫id
 * @param data       {id_list:[],hit_handling_method:'directly_return|optimization'}
 * @param loading
 * @returns
 */
const batchEditHitHandling: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}/document/batch_hit_handling`, data, undefined, loading)
}

/**
 * 獲得QA模版
 * @param 參數 fileName,type,
 */
const exportQATemplate: (fileName: string, type: string, loading?: Ref<boolean>) => void = (
  fileName,
  type,
  loading
) => {
  return exportExcel(fileName, `${prefix}/document/template/export`, { type }, loading)
}

/**
 * 導出文檔
 * @param document_name 文檔名稱
 * @param dataset_id    數據集id
 * @param document_id   文檔id
 * @param loading       加載器
 * @returns
 */
const exportDocument: (
  document_name: string,
  dataset_id: string,
  document_id: string,
  loading?: Ref<boolean>
) => Promise<any> = (document_name, dataset_id, document_id, loading) => {
  return exportExcel(
    document_name + '.xls',
    `${prefix}/${dataset_id}/document/${document_id}/export`,
    {},
    loading
  )
}

export default {
  postSplitDocument,
  getDocument,
  getAllDocument,
  postDocument,
  putDocument,
  delDocument,
  delMulDocument,
  getDocumentDetail,
  listSplitPattern,
  putDocumentRefresh,
  putDocumentSync,
  delMulSyncDocument,
  postWebDocument,
  putMigrateMulDocument,
  batchEditHitHandling,
  exportQATemplate,
  postQADocument,
  exportDocument
}
