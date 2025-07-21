import { Result } from '@/request/Result'
import { get, post, del, put, exportFile, exportExcel } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'

const prefix = '/system/resource/knowledge'

/**
 * 知识库列表（无分页）
 * @param 参数
 * param  {
 "folder_id": "string",
 "name": "string",
 "tool_type": "string",
 desc: string,
 }
 */
const getKnowledgeList: (param?: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  param,
  loading,
) => {
  return get(`${prefix}`, param, loading)
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
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 知识库详情
 * @param 参数 knowledge_id
 */
const getKnowledgeDetail: (knowledge_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  loading,
) => {
  return get(`${prefix}/${knowledge_id}`, undefined, loading)
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
  return put(`${prefix}/${knowledge_id}`, data, undefined, loading)
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
  return put(`${prefix}/${knowledge_id}/embedding`, undefined, undefined, loading)
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
    `${prefix}/${knowledge_id}/export`,
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
    `${prefix}/${knowledge_id}/export_zip`,
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
const putKnowledgeHitTest: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, data, loading) => {
  return put(`${prefix}/${knowledge_id}/hit_test`, data, undefined, loading)
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
  return put(`${prefix}/${knowledge_id}/sync`, undefined, { sync_type }, loading)
}


/**
 * 获取当前用户可使用的向量化模型列表（没用到）
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
const getKnowledgeModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix}/model`, loading)
}

const putLarkKnowledge: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return put(`${prefix}/lark/${knowledge_id}`, data, undefined, loading)
}


export default {
  getKnowledgeList,
  getKnowledgeListPage,
  getKnowledgeDetail,
  putKnowledge,
  delKnowledge,
  putReEmbeddingKnowledge,
  exportKnowledge,
  exportZipKnowledge,
  putGenerateRelated,
  putKnowledgeHitTest,
  putSyncWebKnowledge,
  getKnowledgeModel,
  putLarkKnowledge
} as {
  [key: string]: any
}
