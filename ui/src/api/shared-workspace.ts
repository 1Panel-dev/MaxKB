import {Result} from '@/request/Result'
import {get, post, del, put, exportFile, exportExcel} from '@/request/index'
import {type Ref} from 'vue'
import type {PageList, pageRequest} from '@/api/type/common'
import type {knowledgeData} from '@/api/type/knowledge'

import useStore from '@/stores'
import type {ChatUserGroupItem} from './type/workspaceChatUser'

const prefix = '/system/shared'
const prefix_workspace: any = {_value: 'workspace/'}
Object.defineProperty(prefix_workspace, 'value', {
  get: function () {
    const {user} = useStore()
    return this._value + user.getWorkspaceId()
  },
})

const getKnowledgeList: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (loading) => {
  return get(`${prefix}/${prefix_workspace.value}/knowledge`, {}, loading)
}

const getKnowledgeListPage: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (page, param, loading) => {
  return get(
    `${prefix}/${prefix_workspace.value}/knowledge/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 知识库详情
 * @param 参数 knowledge_id
 */
const getKnowledgeDetail: (knowledge_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  loading,
) => {
  return get(`${prefix}/${prefix_workspace.value}/knowledge/${knowledge_id}`, undefined, loading)
}

/**
 * 文档分页列表
 * @param 参数  knowledge_id,
 * param {
 "name": "string",
 folder_id: "string",
 }
 */

const getDocumentPage: (
  knowledge_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, page, param, loading) => {
  return get(
    `${prefix}/${prefix_workspace.value}/knowledge/${knowledge_id}/document/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 文档详情
 * @param 参数 knowledge_id
 */
const getDocumentDetail: (
  knowledge_id: string,
  document_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, loading) => {
  return get(
    `${prefix}/${prefix_workspace.value}/knowledge/${knowledge_id}/document/${document_id}`,
    {},
    loading,
  )
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
    `${prefix}/${prefix_workspace.value}/knowledge/${knowledge_id}/problem/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 获取工作空间下共享知识库用户组的用户列表
 */
const getUserGroupUserList: (
  resource: any,
  user_group_id: string,
  page: pageRequest,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<PageList<ChatUserGroupItem[]>>> = (resource, user_group_id, page, params, loading) => {
  return get(
    `${prefix}/${prefix_workspace.value}/KNOWLEDGE/${resource.resource_id}/user_group_id/${user_group_id}/${page.current_page}/${page.page_size}`,
    params, loading,
  )
}

/**
 * 获取工作空间下共享知识库的用户组
 */
const getUserGroupList: (resource: any, loading?: Ref<boolean>) => Promise<Result<ChatUserGroupItem[]>> = (resource, loading) => {
  return get(`${prefix}/${prefix_workspace.value}/KNOWLEDGE/${resource.resource_id}/user_group`, undefined, loading)
}

/**
 * 段落分页列表
 * @param 参数 knowledge_id document_id
 * param {
 "title": "string",
 "content": "string",
 }
 */
const getParagraphPage: (
  knowledge_id: string,
  document_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (knowledge_id, document_id, page, param, loading) => {
  return get(
    `${prefix}/${prefix_workspace.value}/knowledge/${knowledge_id}/document/${document_id}/paragraph/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

const getModelList: (param: any, loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  param: any,
  loading,
) => {
  return get(`${prefix}/${prefix_workspace.value}/model`, param, loading)
}

const getToolList: (param: any, loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (param, loading) => {
  return get(`${prefix}/${prefix_workspace.value}/tool`, param, loading)
}

const getToolListPage: (
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(
    `${prefix}/${prefix_workspace.value}/tool/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 获取全部用户
 */
const getAllMemberList: (arg: string, loading?: Ref<boolean>) => Promise<Result<Record<string, any>[]>> = (
  arg,
  loading,
) => {
  return get('/user/list', undefined, loading)
}

const getTags: (knowledge_id: string, params: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  knowledge_id,
  params,
  loading,
) => {
  return get(`${prefix}/${prefix_workspace.value}/knowledge/${knowledge_id}/tags`, params, loading)
}

export default {
  getKnowledgeList,
  getKnowledgeListPage,
  getKnowledgeDetail,
  getProblemsPage,
  getDocumentPage,
  getDocumentDetail,
  getParagraphPage,
  getModelList,
  getToolList,
  getToolListPage,
  getUserGroupList,
  getUserGroupUserList,
  getAllMemberList,
  getTags
}
