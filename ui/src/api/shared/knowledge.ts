import { Result } from '@/request/Result'
import { get, post, del, put, exportFile, exportExcel } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
import type { knowledgeData } from '@/api/type/knowledge'

const prefix = '/system/shared'
const workspace_id = localStorage.getItem('workspace_id') || 'default'
const getSharedWorkspaceKnowledge: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  loading,
) => {
  return get(`${prefix}/workspace/${workspace_id}/knowledge`, {}, loading)
}

const getSharedWorkspaceKnowledgePage: (
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (param: any, loading) => {
  return get(`${prefix}/workspace/${workspace_id}/knowledge`, param, loading)
}

const getSharedAuthorizationKnowledgeGet: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/knowledge/${knowledge_id}/authorization`, {}, loading)
}

const getSharedAuthorizationKnowledgePost: (
  knowledge_id: string,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, param, loading) => {
  return post(`${prefix}/knowledge/${knowledge_id}/authorization`, param, loading)
}

const getSharedAuthorizationToolGet: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/tool/${knowledge_id}/authorization`, {}, loading)
}

const getSharedAuthorizationToolPost: (
  knowledge_id: string,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, param, loading) => {
  return post(`${prefix}/tool/${knowledge_id}/authorization`, param, loading)
}

const getSharedAuthorizationModelGet: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/model/${knowledge_id}/authorization`, {}, loading)
}

const getSharedAuthorizationModelPost: (
  knowledge_id: string,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, param, loading) => {
  return post(`${prefix}/model/${knowledge_id}/authorization`, param, loading)
}

/**
 * 获得知识库文件夹列表
 * @params 参数
 * {folder_id: string,
 * name: string,
 * user_id: string，
 * desc: string,}
 */
const getKnowledgeByFolder: (data?: any, loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  data,
  loading,
) => {
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
  return get(`${prefix}/knowledge/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 知识库详情
 * @param 参数 knowledge_id
 */
const getKnowledgeDetail: (knowledge_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  loading,
) => {
  return get(`${prefix}/knowledge/${knowledge_id}`, undefined, loading)
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

/**
 * 删除知识库
 * @param 参数 knowledge_id
 */
const delKnowledge: (knowledge_id: String, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  knowledge_id,
  loading,
) => {
  return del(`${prefix}/${knowledge_id}`, undefined, {}, loading)
}

/**
 * 向量化知识库
 * @param 参数 knowledge_id
 */
const putReEmbeddingKnowledge: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, loading) => {
  return put(`${prefix}/knowledge/${knowledge_id}/embedding`, undefined, undefined, loading)
}

/**
 * 导出知识库
 * @param knowledge_name 知识库名称
 * @param knowledge_id   知识库id
 * @returns
 */
const exportKnowledge: (
  knowledge_name: string,
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<any> = (knowledge_name, knowledge_id, loading) => {
  return exportExcel(
    knowledge_name + '.xlsx',
    `${prefix}/${knowledge_id}/knowledge/${knowledge_id}/export`,
    undefined,
    loading,
  )
}
/**
 *导出Zip知识库
 * @param knowledge_name 知识库名称
 * @param knowledge_id   知识库id
 * @param loading      加载器
 * @returns
 */
const exportZipKnowledge: (
  knowledge_name: string,
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<any> = (knowledge_name, knowledge_id, loading) => {
  return exportFile(
    knowledge_name + '.zip',
    `${prefix}/${knowledge_id}/knowledge/${knowledge_id}/export_zip`,
    undefined,
    loading,
  )
}

/**
 * 生成关联问题
 * @param knowledge_id 知识库id
 * @param data
 * @param loading
 * @returns
 */
const putGenerateRelated: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, data, loading) => {
  return put(`${prefix}/${knowledge_id}/generate_related`, data, null, loading)
}

/**
 * 命中测试列表
 * @param knowledge_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getKnowledgeHitTest: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, data, loading) => {
  return get(`${prefix}/${knowledge_id}/hit_test`, data, loading)
}

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
  return put(`${prefix}/knowledge/${knowledge_id}/sync`, undefined, { sync_type }, loading)
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
const postKnowledge: (data: knowledgeData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}/knowledge/base`, data, undefined, loading, 1000 * 60 * 5)
}

/**
 * 获取当前用户可使用的向量化模型列表
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getKnowledgeEmdeddingModel: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/${knowledge_id}/emdedding_model`, loading)
}

/**
 * 获取当前用户可使用的模型列表
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getKnowledgeModel: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/${knowledge_id}/model`, loading)
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
const postWebKnowledge: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}/knowledge/web`, data, undefined, loading)
}

/**
 * 获取全部知识库
 * @param 参数
 */
const getAllKnowledge: (loading?: Ref<boolean>) => Promise<Result<any[]>> = (loading) => {
  return get(`${prefix}/knowledge`, undefined, loading)
}

/**
 * 获取飞书文档列表
 * @param knowledge_id
 * @param folder_token
 * @param loading
 * @returns
 */
const getLarkDocumentList: (
  knowledge_id: string,
  folder_token: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, folder_token, data, loading) => {
  return post(`${prefix}/lark/${knowledge_id}/${folder_token}/doc_list`, data, null, loading)
}

const importLarkDocument: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, data, loading) => {
  return post(`${prefix}/lark/${knowledge_id}/import`, data, null, loading)
}

export default {
  getKnowledgeByFolder,
  getKnowledgeList,
  getKnowledgeDetail,
  putKnowledge,
  delKnowledge,
  putReEmbeddingKnowledge,
  exportKnowledge,
  exportZipKnowledge,
  putGenerateRelated,
  getKnowledgeHitTest,
  putSyncWebKnowledge,
  postKnowledge,
  getKnowledgeModel,
  postWebKnowledge,

  getLarkDocumentList,
  importLarkDocument,
  getAllKnowledge,
  getSharedWorkspaceKnowledge,
  getSharedWorkspaceKnowledgePage,
  getSharedAuthorizationKnowledgeGet,
  getSharedAuthorizationKnowledgePost,
  getSharedAuthorizationToolGet,
  getSharedAuthorizationToolPost,
  getSharedAuthorizationModelGet,
  getSharedAuthorizationModelPost,
}
