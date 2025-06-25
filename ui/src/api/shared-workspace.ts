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
  getModelList,
  getToolList,
  getToolListPage
}
