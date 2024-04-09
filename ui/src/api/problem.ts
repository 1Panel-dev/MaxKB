import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { Ref } from 'vue'
import type { KeyValue } from '@/api/type/common'
import type { pageRequest } from '@/api/type/common'
const prefix = '/dataset'

/**
 * 文档分页列表
 * @param 参数  dataset_id,   
 * page {
              "current_page": "string",
              "page_size": "string",
            }
* query {
          "content": "string",
        }
 */

const getProblems: (
  dataset_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, page, param, loading) => {
  return get(
    `${prefix}/${dataset_id}/problem/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

/**
 * 创建问题
 * @param 参数 dataset_id
 * data: array[string]
 */
const postProblems: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return post(`${prefix}/${dataset_id}/problem`, data, undefined, loading)
}

/**
 * 删除问题
 * @param 参数 dataset_id, problem_id,
 */
const delProblems: (
  dataset_id: string,
  problem_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, problem_id, loading) => {
  return del(`${prefix}/${dataset_id}/problem/${problem_id}`, loading)
}

/**
 * 批量删除问题
 * @param 参数 dataset_id,
 */
const delMulProblem: (
  dataset_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return del(`${prefix}/${dataset_id}/problem/_batch`, undefined, data, loading)
}

/**
 * 修改问题
 * @param 参数 
 * dataset_id, problem_id, 
 * {
      "content": "string",
    }
 */
const putProblems: (
  dataset_id: string,
  problem_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, problem_id, data: any, loading) => {
  return put(`${prefix}/${dataset_id}/problem/${problem_id}`, data, undefined, loading)
}

/**
 * 问题详情
 * @param 参数
 * dataset_id, problem_id,
 */
const getDetailProblems: (
  dataset_id: string,
  problem_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, problem_id, loading) => {
  return get(`${prefix}/${dataset_id}/problem/${problem_id}/paragraph`, undefined, loading)
}

export default {
  getProblems,
  postProblems,
  delProblems,
  putProblems,
  getDetailProblems,
  delMulProblem
}
