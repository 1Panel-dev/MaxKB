import {Result} from '@/request/Result'
import {get, post, del, put, exportFile, exportExcel} from '@/request/index'
import {type Ref} from 'vue'
import type {pageRequest} from '@/api/type/common'
import type {knowledgeData} from '@/api/type/knowledge'

import useStore from '@/stores'

const prefix = '/system/resource'
const prefix_workspace: any = {_value: 'workspace/'}
Object.defineProperty(prefix_workspace, 'value', {
  get: function () {
    const {user} = useStore()
    return this._value + user.getWorkspaceId()
  },
})

const getSharedWorkspaceKnowledge: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  loading,
) => {
  return get(`${prefix}/${prefix_workspace.value}/knowledge`, {}, loading)
}

const getSharedWorkspaceKnowledgePage: (
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

const getSharedWorkspaceModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  loading,
) => {
  return get(`${prefix}/${prefix_workspace.value}/model`, {}, loading)
}

const getCESharedWorkspaceModel: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  loading,
) => {
  return get(`/${prefix_workspace.value}/model`, {}, loading)

}

const getSharedWorkspaceModelPage: (
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (param: any, loading) => {
  console.log(`${prefix}/${prefix_workspace.value}/model`)
  return get(`${prefix}/${prefix_workspace.value}/model`, param, loading)
}

const getSharedWorkspaceTool: (loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  loading,
) => {
  return get(`${prefix}/${prefix_workspace.value}/tool`, {}, loading)
}

const getSharedWorkspaceToolPage: (
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (param: any, loading) => {
  return get(`${prefix}/${prefix_workspace.value}/tool`, param, loading)
}

export default {
  getSharedWorkspaceKnowledge,
  getSharedWorkspaceKnowledgePage,
  getSharedWorkspaceModel,
  getSharedWorkspaceModelPage,
  getSharedWorkspaceTool,
  getSharedWorkspaceToolPage,
  getCESharedWorkspaceModel
}
