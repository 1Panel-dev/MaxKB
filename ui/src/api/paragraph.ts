import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
const prefix = '/dataset'

/**
 * 段落列表
 * @param 参数 dataset_id
 */
const getParagraph: (dataset_id: string, document_id: string) => Promise<Result<any>> = (
  dataset_id,
  document_id
) => {
  return get(`${prefix}/${dataset_id}/document/${document_id}/paragraph`)
}

/**
 * 删除段落
 * @param 参数 dataset_id, document_id, paragraph_id
 */
const delParagraph: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string
) => Promise<Result<boolean>> = (dataset_id, document_id, paragraph_id) => {
  return del(`${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}`)
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
  data: any
) => Promise<Result<any>> = (dataset_id, document_id, data: any) => {
  return post(`${prefix}/${dataset_id}/document/${document_id}/paragraph`, data)
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
  data: any
) => Promise<Result<any>> = (dataset_id, document_id, paragraph_id, data: any) => {
  return put(`${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}`, data)
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
  data: any
) => Promise<Result<any>> = (dataset_id, document_id, paragraph_id, data: any) => {
  return post(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}/problem`,
    data
  )
}
/**
 * 删除问题
 * @param 参数 dataset_id, document_id, paragraph_id,problem_id
 */
const delProblem: (
  dataset_id: string,
  document_id: string,
  paragraph_id: string,
  problem_id: string
) => Promise<Result<boolean>> = (dataset_id, document_id, paragraph_id, problem_id) => {
  return del(
    `${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}/problem/${problem_id}`
  )
}

export default {
  getParagraph,
  delParagraph,
  putParagraph,
  postParagraph,
  getProblem,
  postProblem,
  delProblem,
}
