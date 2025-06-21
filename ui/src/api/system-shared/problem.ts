import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'

const prefix = '/system/shared/knowledge'

/**
 * 创建问题
 * @param 参数 knowledge_id
 * data: array[string]
 */
const postProblems: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return post(`${prefix}/${knowledge_id}/problem`, data, undefined, loading)
}

/**
 * 问题分页列表
 * @param 参数  knowledge_id,
 * query {
     "content": "string",
   }
 */

const getProblemsPage: (
  knowledge_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, page, param, loading) => {
  return get(
    `${prefix}/${knowledge_id}/problem/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 修改问题
 * @param 参数
 * knowledge_id, problem_id,
 * {
 "content": "string",
 }
 */
const putProblems: (
  knowledge_id: string,
  problem_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, problem_id, data: any, loading) => {
  return put(`${prefix}/${knowledge_id}/problem/${problem_id}`, data, undefined, loading)
}

/**
 * 删除问题
 * @param 参数 knowledge_id, problem_id,
 */
const delProblems: (
  knowledge_id: string,
  problem_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, problem_id, loading) => {
  return del(`${prefix}/${knowledge_id}/problem/${problem_id}`, loading)
}

/**
 * 问题详情
 * @param 参数
 * knowledge_id, problem_id,
 */
const getDetailProblems: (
  knowledge_id: string,
  problem_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, problem_id, loading) => {
  return get(`${prefix}/${knowledge_id}/problem/${problem_id}/paragraph`, undefined, loading)
}

/**
 * 批量关联段落
 * @param 参数 knowledge_id,
 * {
      "problem_id_list": "Array",
      "paragraph_list": "Array",
    }
 */
const putMulAssociationProblem: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(`${prefix}/${knowledge_id}/problem/batch_association`, data, undefined, loading)
}

/**
 * 批量删除问题
 * @param 参数 knowledge_id,
 * data: array[string]
 */
const putMulProblem: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(`${prefix}/${knowledge_id}/problem/batch_delete`, data, undefined, loading)
}

export default {
  postProblems,
  getProblemsPage,
  putProblems,
  delProblems,
  getDetailProblems,
  putMulAssociationProblem,
  putMulProblem,
}
