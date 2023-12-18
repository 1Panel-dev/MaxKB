import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { datasetData } from '@/api/type/dataset'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'
const prefix = '/dataset'

/**
 * 获取分页知识库
 * @param 参数  
 * page {
          "current_page": "string",
          "page_size": "string",
        }
 * param {
          "name": "string",
        }
 */
const getDateset: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 获取全部知识库
 * @param 参数
 */
const getAllDateset: (loading?: Ref<boolean>) => Promise<Result<any[]>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 删除知识库
 * @param 参数 dataset_id
 */
const delDateset: (dataset_id: String, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  dataset_id,
  loading
) => {
  return del(`${prefix}/${dataset_id}`, undefined, {}, loading)
}

/**
 * 创建知识库
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
 * 知识库详情
 * @param 参数 dataset_id
 */
const getDatesetDetail: (dataset_id: string) => Promise<Result<any>> = (dataset_id) => {
  return get(`${prefix}/${dataset_id}`)
}

/**
 * 修改知识库信息
 * @param 参数 
 * dataset_id
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
 * 获取知识库 可关联的应用列表
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
export default {
  getDateset,
  getAllDateset,
  delDateset,
  postDateset,
  getDatesetDetail,
  putDateset,
  listUsableApplication
}
