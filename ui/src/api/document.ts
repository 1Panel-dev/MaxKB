import { Result } from '@/request/Result'
import { get, post, del, put, exportExcel } from '@/request/index'
import type { Ref } from 'vue'
import type { KeyValue } from '@/api/type/common'
import type { pageRequest } from '@/api/type/common'
const prefix = '/dataset'

/**
 * 分段预览（上传文档）
 * @param 参数  file:file,limit:number,patterns:array,with_filter:boolean
 */
const postSplitDocument: (data: any) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/document/split`, data, undefined, undefined, 1000 * 60 * 60)
}

/**
 * 分段标识列表
 * @param loading 加载器
 * @returns 分段标识列表
 */
const listSplitPattern: (
  loading?: Ref<boolean>
) => Promise<Result<Array<KeyValue<string, string>>>> = (loading) => {
  return get(`${prefix}/document/split_pattern`, {}, loading)
}

/**
 * 文档分页列表
 * @param 参数  dataset_id,   
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
 * 创建批量文档
 * @param 参数 
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
 * 修改文档
 * @param 参数 
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
 * 删除文档
 * @param 参数 dataset_id, document_id,
 */
const delDocument: (
  dataset_id: string,
  document_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, document_id, loading) => {
  return del(`${prefix}/${dataset_id}/document/${document_id}`, loading)
}
/**
 * 批量删除文档
 * @param 参数 dataset_id,
 */
const delMulDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return del(`${prefix}/${dataset_id}/document/_bach`, undefined, { id_list: data }, loading)
}
/**
 * 文档详情
 * @param 参数 dataset_id
 */
const getDocumentDetail: (dataset_id: string, document_id: string) => Promise<Result<any>> = (
  dataset_id,
  document_id
) => {
  return get(`${prefix}/${dataset_id}/document/${document_id}`)
}

/**
 * 刷新文档向量库
 * @param 参数
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
 * 同步web站点类型
 * @param 参数
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
 * 批量同步文档
 * @param 参数 dataset_id,
 */
const delMulSyncDocument: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}/document/_bach`, { id_list: data }, undefined, loading)
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
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/document/web`, data, undefined, loading)
}

/**
 * 导入QA文档
 * @param 参数 
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
 * 批量迁移文档
 * @param 参数 dataset_id,target_dataset_id,
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
 * @param dataset_id 知识库id
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
 * 获得QA模版
 * @param 参数 fileName,type,
 */
const exportQATemplate: (fileName: string, type: string, loading?: Ref<boolean>) => void = (
  fileName,
  type,
  loading
) => {
  return exportExcel(fileName, `${prefix}/document/template/export`, { type }, loading)
}

/**
 * 导出文档
 * @param document_name 文档名称
 * @param dataset_id    数据集id
 * @param document_id   文档id
 * @param loading       加载器
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
