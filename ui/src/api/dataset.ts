import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { datasetListRequest, datasetData } from '@/api/type/dataset'

const prefix = '/dataset'

/**
 * 获取分页数据集
 * @param 参数  {
              "current_page": "string",
              "page_size": "string",
              "name": "string",
            }
 */
const getDateset: (param: datasetListRequest) => Promise<Result<any>> = (param) => {
  return get(
    `${prefix}/${param.current_page}/${param.page_size}`,
    param.name && { name: param.name }
  )
}

/**
 * 获取全部数据集
 * @param 参数 name
 */
const getAllDateset: (param?: string) => Promise<Result<any[]>> = (param) => {
  return get(`${prefix}`, param && { name: param })
}

/**
 * 删除数据集
 * @param 参数 dataset_id
 */
const delDateset: (dataset_id: String) => Promise<Result<boolean>> = (dataset_id) => {
  return del(`${prefix}/${dataset_id}`)
}

/**
 * 创建数据集
 * @param 参数 
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
const postDateset: (data: datasetData) => Promise<Result<any>> = (data) => {
  return post(`${prefix}`, data)
}

/**
 * 数据集详情
 * @param 参数 dataset_id
 */
const getDatesetDetail: (dataset_id: string) => Promise<Result<any>> = (dataset_id) => {
  return get(`${prefix}/${dataset_id}`)
}

/**
 * 修改数据集信息
 * @param 参数 
 * dataset_id, document_id, 
 * {
      "name": "string",
      "desc": true
    }
 */
const putDateset: (dataset_id: string, data: any) => Promise<Result<any>> = (
  dataset_id,
  data: any
) => {
  return put(`${prefix}/${dataset_id}`, data)
}

/**
 * 分段预览（上传文档）
 * @param 参数  file:file,limit:number,patterns:array,with_filter:boolean
 */
const postSplitDocument: (data: any) => Promise<Result<any>> = (data) => {
  return post(`${prefix}/document/split`, data)
}

/**
 * 文档列表
 * @param 参数  dataset_id, name
 */

const getDocument: (dataset_id: string, name?: string) => Promise<Result<any>> = (
  dataset_id,
  name
) => {
  return get(`${prefix}/${dataset_id}/document`, name && { name })
}

/**
 * 创建文档
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
const postDocument: (dataset_id: string, data: any) => Promise<Result<any>> = (
  dataset_id,
  data
) => {
  return post(`${prefix}/${dataset_id}/document`, data)
}

/**
 * 修改文档
 * @param 参数 
 * dataset_id, document_id, 
 * {
      "name": "string",
      "is_active": true
    }
 */
const putDocument: (dataset_id: string, document_id: string, data: any) => Promise<Result<any>> = (
  dataset_id,
  document_id,
  data: any
) => {
  return put(`${prefix}/${dataset_id}/document/${document_id}`, data)
}

/**
 * 删除文档
 * @param 参数 dataset_id, document_id,
 */
const delDocument: (dataset_id: string, document_id: string) => Promise<Result<boolean>> = (
  dataset_id,
  document_id
) => {
  return del(`${prefix}/${dataset_id}/document/${document_id}`)
}

export default {
  getDateset,
  getAllDateset,
  delDateset,
  postDateset,
  getDatesetDetail,
  putDateset,
  postSplitDocument,
  getDocument,
  postDocument,
  putDocument,
  delDocument
}
