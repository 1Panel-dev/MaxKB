import { Result } from '@/request/Result'
import { get, post, del, put, exportFile, exportExcel } from '@/request/index'
import { type Ref } from 'vue'

const prefix = '/system/shared'

const getSharedAuthorizationKnowledge: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/knowledge/${knowledge_id}/authorization`, {}, loading)
}

const postSharedAuthorizationKnowledge: (
  knowledge_id: string,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, param, loading) => {
  return post(`${prefix}/knowledge/${knowledge_id}/authorization`, param, loading)
}

const getSharedAuthorizationTool: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/tool/${knowledge_id}/authorization`, {}, loading)
}

const postSharedAuthorizationTool: (
  knowledge_id: string,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, param, loading) => {
  return post(`${prefix}/tool/${knowledge_id}/authorization`, param, loading)
}

const getSharedAuthorizationModel: (
  knowledge_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, loading) => {
  return get(`${prefix}/model/${knowledge_id}/authorization`, {}, loading)
}

const postSharedAuthorizationModel: (
  knowledge_id: string,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (knowledge_id, param, loading) => {
  return post(`${prefix}/model/${knowledge_id}/authorization`, param, loading)
}

export default {
  getSharedAuthorizationKnowledge,
  postSharedAuthorizationKnowledge,
  getSharedAuthorizationTool,
  postSharedAuthorizationTool,
  getSharedAuthorizationModel,
  postSharedAuthorizationModel,
} as {
  [key: string]: any
}
