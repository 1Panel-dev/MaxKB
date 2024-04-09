import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { Ref } from 'vue'
const prefix = '/dataset'

/**
 * 段落列表
 * @param 参数 dataset_id document_id
 * page {
              "current_page": "string",
              "page_size": "string",
            }
 * param {
          "title": "string",
          "content": "string",
        }
 */
const getParagraph: (
  dataset_id: string,
  document_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, page, param, loading) => {
  return get(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

/**
 * 删除段落
 * @param 参数 dataset_id, document_id, paragraph_id
 */
const delParagraph: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, document_id, paragraph_id, loading) => {
  return del(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}`,
    undefined,
    {},
    loading
  )
}

/**
 * 创建段落
 * @param 参数 
 * dataset_id, document_id
 * {
  "content": "string",
  "title": "string",
  "is_active": true,
  "problem_list": [
    {
      "id": "string",
      "content": "string"
    }
  ]
    }
 */
const postParagraph: (
  dataset_id: string,
  document_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/document/${document_id}/paragraph`, data, undefined, loading)
}

/**
 * 修改段落
 * @param 参数 
 * dataset_id, document_id, paragraph_id
 * {
  "content": "string",
  "title": "string",
  "is_active": true,
  "problem_list": [
    {
      "id": "string",
      "content": "string"
    }
  ]
    }
 */
const putParagraph: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, paragraph_id, data, loading) => {
  return put(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}`,
    data,
    undefined,
    loading
  )
}

/**
 * 问题列表
 * @param 参数 dataset_id，document_id，paragraph_id
 */
const getProblem: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string
) => Promise<Result<any>> = (dataset_id, document_id, paragraph_id: string) => {
  return get(`${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}/problem`)
}

/**
 * 创建问题
 * @param 参数 
 * dataset_id, document_id, paragraph_id
 * {
      "id": "string",
      content": "string"
    }
 */
const postProblem: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, paragraph_id, data: any, loading) => {
  return post(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}/problem`,
    data,
    {},
    loading
  )
}
/**
 *
 * @param dataset_id 数据集id
 * @param document_id 文档id
 * @param paragraph_id 段落id
 * @param problem_id 问题id
 * @param loading 加载器
 * @returns
 */
const associationProblem: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string,
  problem_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, paragraph_id, problem_id, loading) => {
  return put(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}/problem/${problem_id}/association`,
    {},
    {},
    loading
  )
}
/**
 * 解除关联问题
 * @param 参数 dataset_id, document_id, paragraph_id,problem_id
 */
const disassociationProblem: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string,
  problem_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, document_id, paragraph_id, problem_id, loading) => {
  return put(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}/problem/${problem_id}/un_association`,
    {},
    {},
    loading
  )
}

export default {
  getParagraph,
  delParagraph,
  putParagraph,
  postParagraph,
  getProblem,
  postProblem,
  disassociationProblem,
  associationProblem
}
