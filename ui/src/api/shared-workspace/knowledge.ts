import { Result } from '@/request/Result'
import { get, post, del, put, exportFile, exportExcel } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
import type { knowledgeData } from '@/api/type/knowledge'

import useStore from '@/stores'
const prefix: any = { _value: '/system/shared/knowledge/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId()
  },
})

/**
 * 知识库列表（无分页）
 * @param 参数
 * param  {
    folder_id: "string",
    name: "string",
    tool_type: "string",
    desc: string,
  }
 */
const getKnowledgeList: (param?: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  param,
  loading,
) => {
  return get(`${prefix.value}`, param, loading)
}

/**
 * 知识库分页列表
 * @param 参数
 * param  {
 "folder_id": "string",
 "name": "string",
 "tool_type": "string",
 desc: string,
 }
 */
const getKnowledgeListPage: (
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix.value}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 知识库详情
 * @param 参数 knowledge_id
 */
const getKnowledgeDetail: (knowledge_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  loading,
) => {
  return get(`${prefix.value}/${knowledge_id}`, undefined, loading)
}

export default {
  getKnowledgeList,
  getKnowledgeListPage,
  getKnowledgeDetail,
}
