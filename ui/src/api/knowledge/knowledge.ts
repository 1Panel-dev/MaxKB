import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
import type { knowledgeData } from '@/api/type/knowledge'
const prefix = '/workspace'

/**
 * 获得知识库文件夹列表
 * @params 参数
 * {folder_id: string,
 * name: string,
 * user_id: string，
 * desc: string,}
 */
const getKnowledgeByFolder: (
  wordspace_id: string,
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (wordspace_id, data, loading) => {
  return get(`${prefix}/${wordspace_id}/knowledge`, data, loading)
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
  wordspace_id: string,
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, page, param, loading) => {
  return get(
    `${prefix}/${wordspace_id}/knowledge/${page.current_page}/${page.page_size}`,
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
  wordspace_id: string,
  knowledge_id: string,
  sync_type: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, knowledge_id, sync_type, loading) => {
  return put(
    `${prefix}/${wordspace_id}/knowledge/${knowledge_id}/sync`,
    undefined,
    { sync_type },
    loading,
  )
}

/**
 * 向量化知识库
 * @param 参数 knowledge_id
 */
const putReEmbeddingDataset: (
  wordspace_id: string,
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, knowledge_id, loading) => {
  return put(
    `${prefix}/${wordspace_id}/knowledge/${knowledge_id}/embedding`,
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
  wordspace_id: string,
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, knowledge_id, loading) => {
  return get(`${prefix}/${wordspace_id}/knowledge/${knowledge_id}`, undefined, loading)
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
const postDataset: (
  wordspace_id: string,
  data: knowledgeData,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, data, loading) => {
  return post(`${prefix}/${wordspace_id}/knowledge/base`, data, undefined, loading, 1000 * 60 * 5)
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
const postWebDataset: (
  wordspace_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, data, loading) => {
  return post(`${prefix}/${wordspace_id}/knowledge/web`, data, undefined, loading)
}
/**
 * 创建Lark知识库
 * @param 参数
 * {
 "name": "string",
 "desc": "string",
 "app_id": "string",
 "app_secret": "string",
 "folder_token": "string",
 }
 */
const postLarkDataset: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}/lark/save`, data, undefined, loading)
}

export default {
  getKnowledgeByFolder,
  getKnowledgeList,
  putReEmbeddingDataset,
  putSyncWebKnowledge,
  getKnowledgeDetail,
  postDataset,
  postWebDataset
}
