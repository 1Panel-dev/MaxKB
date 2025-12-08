import { Result } from '@/request/Result'
import { get, post, del, put, exportFile, exportExcel } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
import type { knowledgeData } from '@/api/type/knowledge'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/knowledge'
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
  return put(`${prefix.value}/${knowledge_id}`, data, undefined, loading)
}

/**
 * 删除知识库
 * @param 参数 knowledge_id
 */
const delKnowledge: (knowledge_id: String, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  knowledge_id,
  loading,
) => {
  return del(`${prefix.value}/${knowledge_id}`, undefined, {}, loading)
}

/**
 * 向量化知识库
 * @param 参数 knowledge_id
 */
const putReEmbeddingKnowledge: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, loading) => {
  return put(`${prefix.value}/${knowledge_id}/embedding`, undefined, undefined, loading)
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
    `${prefix.value}/${knowledge_id}/export`,
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
    `${prefix.value}/${knowledge_id}/export_zip`,
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
  return put(`${prefix.value}/${knowledge_id}/generate_related`, data, null, loading)
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
  return put(`${prefix.value}/${knowledge_id}/hit_test`, data, undefined, loading)
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
  return put(`${prefix.value}/${knowledge_id}/sync`, undefined, { sync_type }, loading)
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
  return post(`${prefix.value}/base`, data, undefined, loading, 1000 * 60 * 5)
}

/**
 * 获取当前用户可使用的向量化模型列表 (没用到)
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getKnowledgeEmdeddingModel: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix.value}/${knowledge_id}/emdedding_model`, loading)
}

/**
 * 获取当前用户可使用的模型列表
 * @param
 * @param loading
 * @returns
 */
const getKnowledgeModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix.value}/model`, loading)
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
  return post(`${prefix.value}/web`, data, undefined, loading)
}

// 创建飞书知识库
const postLarkKnowledge: (data: any, loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  data,
  loading,
) => {
  return post(`${prefix.value}/lark/save`, data, null, loading)
}

const putLarkKnowledge: (
  knowledge_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (knowledge_id, data, loading) => {
  return put(`${prefix.value}/lark/${knowledge_id}`, data, undefined, loading)
}

const getAllTags: (params: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  params,
  loading,
) => {
  return get(`${prefix.value}/tags`, params, loading)
}

const getTags: (knowledge_id: string, params: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  params,
  loading,
) => {
  return get(`${prefix.value}/${knowledge_id}/tags`, params, loading)
}

const postTags: (knowledge_id: string, tags: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  tags,
  loading,
) => {
  return post(`${prefix.value}/${knowledge_id}/tags`, tags, null, loading)
}

const putTag: (knowledge_id: string, tag_id: string, tag: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  tag_id,
  tag,
  loading,
) => {
  return put(`${prefix.value}/${knowledge_id}/tags/${tag_id}`, tag, null, loading)
}

const delTag: (knowledge_id: string, tag_id: string, type: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  tag_id,
  type,
  loading,
) => {
  return del(`${prefix.value}/${knowledge_id}/tags/${tag_id}/${type}`, null, loading)
}

const delMulTag: (knowledge_id: string, tags: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  tags,
  loading,
) => {
  return put(`${prefix.value}/${knowledge_id}/tags/batch_delete`, tags, null, loading)
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
  postKnowledge,
  getKnowledgeModel,
  postWebKnowledge,
  postLarkKnowledge,
  putLarkKnowledge,
  getAllTags,
  getTags,
  postTags,
  putTag,
  delTag,
  delMulTag
}
