import { Result } from '@/request/Result'
import { get, post, del, put, exportExcel } from '@/request/index'
import type { datasetData } from '@/api/type/dataset'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'
const prefix = '/dataset'

/**
 * 獲取分頁知識庫
 * @param 參數  
 * page {
          "current_page": "string",
          "page_size": "string",
        }
 * param {
          "name": "string",
        }
 */
const getDataset: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 獲取全部知識庫
 * @param 參數
 */
const getAllDataset: (loading?: Ref<boolean>) => Promise<Result<any[]>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 刪除知識庫
 * @param 參數 dataset_id
 */
const delDataset: (dataset_id: String, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  dataset_id,
  loading
) => {
  return del(`${prefix}/${dataset_id}`, undefined, {}, loading)
}

/**
 * 創建知識庫
 * @param 參數 
 * {
  "name": "string",
  "desc": "string",
  "documents": [
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
          ]
        }
      ]
    }
  ]
}
 */
const postDataset: (data: datasetData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading, 1000 * 60 * 5)
}

/**
 * 創建Web知識庫
 * @param 參數 
 * {
  "name": "string",
  "desc": "string",
  "source_url": "string",
  "selector": "string",
}
 */
const postWebDataset: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/web`, data, undefined, loading)
}

/**
 * 創建QA知識庫
  * @param 參數 formData
 * {
  "file": "file",
  "name": "string",
  "desc": "string",
  }
 */
const postQADataset: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/qa`, data, undefined, loading)
}

/**
 * 知識庫詳情
 * @param 參數 dataset_id
 */
const getDatasetDetail: (dataset_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  dataset_id,
  loading
) => {
  return get(`${prefix}/${dataset_id}`, undefined, loading)
}

/**
 * 修改知識庫信息
 * @param 參數 
 * dataset_id
 * {
      "name": "string",
      "desc": true
    }
 */
const putDataset: (dataset_id: string, data: any) => Promise<Result<any>> = (
  dataset_id,
  data: any
) => {
  return put(`${prefix}/${dataset_id}`, data)
}
/**
 * 獲取知識庫 可關聯的應用列表
 * @param dataset_id
 * @param loading
 * @returns
 */
const listUsableApplication: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<ApplicationFormType>>> = (dataset_id, loading) => {
  return get(`${prefix}/${dataset_id}/application`, {}, loading)
}

/**
 * 命中測試列表
 * @param dataset_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getDatasetHitTest: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (dataset_id, data, loading) => {
  return get(`${prefix}/${dataset_id}/hit_test`, data, loading)
}

/**
 * 同步知識庫
 * @param 參數 dataset_id
 * @query 參數 sync_type // 同步類型->replace:替換同步,complete:完整同步
 */
const putSyncWebDataset: (
  dataset_id: string,
  sync_type: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, sync_type, loading) => {
  return put(`${prefix}/${dataset_id}/sync_web`, undefined, { sync_type }, loading)
}

/**
 * 重新向量化知識庫
 * @param 參數 dataset_id
 */
const putReEmbeddingDataset: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, loading) => {
  return put(`${prefix}/${dataset_id}/re_embedding`, undefined, undefined, loading)
}

/**
 * 導出知識庫
 * @param dataset_name 知識庫名稱
 * @param dataset_id   知識庫id
 * @returns
 */
const exportDataset: (
  dataset_name: string,
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<any> = (dataset_name, dataset_id, loading) => {
  return exportExcel(dataset_name + '.xls', `dataset/${dataset_id}/export`, undefined, loading)
}

export default {
  getDataset,
  getAllDataset,
  delDataset,
  postDataset,
  getDatasetDetail,
  putDataset,
  listUsableApplication,
  getDatasetHitTest,
  postWebDataset,
  putSyncWebDataset,
  putReEmbeddingDataset,
  postQADataset,
  exportDataset
}
