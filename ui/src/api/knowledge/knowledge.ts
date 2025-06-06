import {Result} from '@/request/Result'
import {get, post, del, put} from '@/request/index'
import {type Ref} from 'vue'
import type {pageRequest} from '@/api/type/common'
import type {knowledgeData} from '@/api/type/knowledge'

const prefix = '/workspace/' + localStorage.getItem('workspace_id')

/**
 * 获得知识库文件夹列表
 * @params 参数
 * {folder_id: string,
 * name: string,
 * user_id: string，
 * desc: string,}
 */
const getKnowledgeByFolder: (
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (data, loading) => {
  return get(`${prefix}/knowledge`, data, loading)
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
const getKnowledgeList: (
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(
    `${prefix}/knowledge/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 获取全部知识库
 * @param 参数
 */
// const getAllDataset: (loading?: Ref<boolean>) => Promise<Result<any[]>> = (loading) => {
//   return get(`${prefix}`, undefined, loading)
// }

/**
 * 同步知识库
 * @param 参数 knowledge_id
 * @query 参数 sync_type // 同步类型->replace:替换同步,complete:完整同步
 */
const putSyncWebKnowledge: (
  knowledge_id: string,
  sync_type: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, sync_type, loading) => {
  return put(
    `${prefix}/knowledge/${knowledge_id}/sync`,
    undefined,
    {sync_type},
    loading,
  )
}

/**
 * 向量化知识库
 * @param 参数 knowledge_id
 */
const putReEmbeddingKnowledge: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, loading) => {
  return put(
    `${prefix}/knowledge/${knowledge_id}/embedding`,
    undefined,
    undefined,
    loading,
  )
}

/**
 * 知识库详情
 * @param 参数 knowledge_id
 */
const getKnowledgeDetail: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, loading) => {
  return get(`${prefix}/knowledge/${knowledge_id}`, undefined, loading)
}

/**
 * 创建知识库
 * @param 参数
 * {
 "name": "string",
 "folder_id": "string",
 "desc": "string",
 "embedding": "string"
 }
 */
const postKnowledge: (
  data: knowledgeData,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}/knowledge/base`, data, undefined, loading, 1000 * 60 * 5)
}

/**
 * 创建Web知识库
 * @param 参数
 * {
 "name": "string",
 "folder_id": "string",
 "desc": "string",
 "embedding": "string",
 "source_url": "string",
 "selector": "string"
 }
 */
const postWebKnowledge: (
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}/knowledge/web`, data, undefined, loading)
}
/**
 * 修改知识库信息
 * @param 参数
 * knowledge_id
 * {
 "name": "string",
 "desc": true
 }
 */
const putKnowledge: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return put(`${prefix}/knowledge/${knowledge_id}`, data, undefined, loading)
}

export default {
  getKnowledgeByFolder,
  getKnowledgeList,
  putReEmbeddingKnowledge,
  putSyncWebKnowledge,
  getKnowledgeDetail,
  postKnowledge,
  postWebKnowledge,
  putKnowledge,
}
