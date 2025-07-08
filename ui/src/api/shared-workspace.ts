import {Result} from '@/request/Result'
import {get, post, del, put, exportFile, exportExcel} from '@/request/index'
import {type Ref} from 'vue'
import type {pageRequest} from '@/api/type/common'
import type {knowledgeData} from '@/api/type/knowledge'

import useStore from '@/stores'

const prefix = '/system/shared'
const prefix_workspace: any = {_value: 'workspace/'}
Object.defineProperty(prefix_workspace, 'value', {
  get: function () {
    const {user} = useStore()
    return this._value + user.getWorkspaceId()
  },
})

const getKnowledgeList: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  loading,
) => {
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
  return get(`${prefix}/${prefix_workspace.value}/knowledge/${knowledge_id}/document/${document_id}`,
    {},
    loading,)
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


const getModelList: (
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (param: any, loading) => {
  return get(`${prefix}/${prefix_workspace.value}/model`, param, loading)
}

const getToolList: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  loading,
) => {
  return get(`${prefix}/${prefix_workspace.value}/tool`, {}, loading)
}

const getToolListPage: (
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${prefix_workspace.value}/tool/${page.current_page}/${page.page_size}`, param, loading)
}

export default {
  getKnowledgeList,
  getKnowledgeListPage,
  getKnowledgeDetail,
  getDocumentPage,
  getDocumentDetail,
  getParagraphPage,
  getModelList,
  getToolList,
  getToolListPage
}
