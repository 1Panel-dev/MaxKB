import { get, put, del, downloadFile } from '@/request/index'
import type { Result } from '@/request/Result'
import type { Ref } from 'vue'

function getWsId(): string { return localStorage.getItem('workspace_id') || 'default' }

const APPLICATION_PREFIX = '/system/resource/application'
const KNOWLEDGE_PREFIX = '/system/resource/knowledge'
const MODEL_PREFIX = '/system/resource/model'
const TOOL_PREFIX = '/system/resource/tool'

/** ---- Application ---- */
const getApplicationList = (
  page: { current_page: number; page_size: number },
  param?: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(`${APPLICATION_PREFIX}/${page.current_page}/${page.page_size}`, param, loading)
}

const delApplication = (id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return del(`${APPLICATION_PREFIX}/${id}`, loading)
}

const getApplicationAccessToken = (id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`${APPLICATION_PREFIX}/${id}/access_token`, undefined, loading)
}

const exportApplication = (id: string, name: string, loading?: Ref<boolean>): Promise<any> => {
  return downloadFile(`${APPLICATION_PREFIX}/${id}/export`, `${name}.mk`, loading)
}

/** ---- Knowledge ---- */
const getKnowledgeList = (
  page: { current_page: number; page_size: number },
  param?: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(`${KNOWLEDGE_PREFIX}/${page.current_page}/${page.page_size}`, param, loading)
}

const delKnowledge = (id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return del(`${KNOWLEDGE_PREFIX}/${id}`, loading)
}

const putReEmbeddingKnowledge = (id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return put(`${KNOWLEDGE_PREFIX}/${id}/embedding`, undefined, loading)
}

/** ---- Model ---- */
const getModelList = (
  page: { current_page: number; page_size: number },
  param?: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(`${MODEL_PREFIX}/${page.current_page}/${page.page_size}`, param, loading)
}

const deleteModel = (id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return del(`${MODEL_PREFIX}/${id}`, loading)
}

/** ---- Tool ---- */
const getToolList = (
  page: { current_page: number; page_size: number },
  param?: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(`${TOOL_PREFIX}/${page.current_page}/${page.page_size}`, param, loading)
}

const getToolById = (id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`${TOOL_PREFIX}/${id}`, undefined, loading)
}

const putTool = (id: string, data: any, loading?: Ref<boolean>): Promise<Result<any>> => {
  return put(`${TOOL_PREFIX}/${id}`, data, loading)
}

const delTool = (id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return del(`${TOOL_PREFIX}/${id}`, loading)
}

/** ---- Common - list workspace users for creator search ---- */
const listUsers = (query?: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`/workspace/${getWsId()}/user`, query ? { nick_name: query } : undefined, loading)
}

export default {
  getApplicationList,
  delApplication,
  getApplicationAccessToken,
  exportApplication,
  getKnowledgeList,
  delKnowledge,
  putReEmbeddingKnowledge,
  getModelList,
  deleteModel,
  getToolList,
  getToolById,
  putTool,
  delTool,
  listUsers,
}
