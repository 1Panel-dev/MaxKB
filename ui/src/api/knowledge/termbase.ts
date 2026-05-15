import { Result } from '@/request/Result'
import { del, get, post, put } from '@/request/index'
import type { Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'

import useStore from '@/stores'

const prefix: any = {_value: '/workspace/'}
Object.defineProperty(prefix, 'value', {
  get: function () {
    const {user} = useStore()
    return this._value + user.getWorkspaceId() + '/knowledge'
  },
})

/**
 * 创建问题
 * @param 参数 knowledge_id
 * data: array[string]
 */
const postTermbase: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return post(`${prefix.value}/${knowledge_id}/termbase`, data, undefined, loading)
}

/**
 * 问题分页列表
 * @param 参数  knowledge_id,
 * query {
 "content": "string",
 }
 */

const getTermbasePage: (
  knowledge_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, page, param, loading) => {
  return get(
    `${prefix.value}/${knowledge_id}/termbase/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 修改问题
 * @param 参数
 * knowledge_id, termbase_id,
 * {
 "content": "string",
 }
 */
const putTermbase: (
  knowledge_id: string,
  termbase_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, termbase_id, data: any, loading) => {
  return put(`${prefix.value}/${knowledge_id}/termbase/${termbase_id}`, data, undefined, loading)
}

/**
 * 删除问题
 * @param 参数 knowledge_id, termbase_id,
 */
const delTermbase: (
  knowledge_id: string,
  termbase_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, termbase_id, loading) => {
  return del(`${prefix.value}/${knowledge_id}/termbase/${termbase_id}`, loading)
}

const putMulTermbase: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (knowledge_id, data, loading) => {
  return put(`${prefix.value}/${knowledge_id}/termbase/batch_delete`, data, undefined, loading)
}

const exportMulTermbase: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return post(`${prefix.value}/${knowledge_id}/termbase/batch_export`, data, undefined, loading)
}

export default {
  postTermbase,
  getTermbasePage,
  putTermbase,
  delTermbase,
  putMulTermbase,
  exportMulTermbase,
}
