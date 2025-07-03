import { Result } from '@/request/Result'
import type { Ref } from 'vue'
import { get, post, del } from '@/request/index'
import type {
  WorkspaceItem,
  CreateWorkspaceMemberParamsItem,
  WorkspaceMemberItem,
} from '@/api/type/workspace'
import type { pageRequest, PageList } from '@/api/type/common'

const prefix = '/workspace'

/**
 * 获取首页的工作空间下拉列表
 */
const getWorkspaceListByUser: (loading?: Ref<boolean>) => Promise<Result<WorkspaceItem[]>> = (
  loading,
) => {
  return get('/workspace/by_user', undefined, loading)
}

/**
 * 获取添加成员时的工作空间下拉列表
 */
const getWorkspaceList: (loading?: Ref<boolean>) => Promise<Result<Record<string, any>[]>> = (
  loading,
) => {
  return get('/workspace/current_user', undefined, loading)
}

/**
 * 获取工作空间列表
 */
const getSystemWorkspaceList: (loading?: Ref<boolean>) => Promise<Result<WorkspaceItem[]>> = (
  loading,
) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 获取工作空间成员列表
 */
const getWorkspaceMemberList: (
  workspace_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<PageList<WorkspaceMemberItem[]>>> = (workspace_id, page, param, loading) => {
  return get(
    `${prefix}/${workspace_id}/user_list/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 获取工作空间全部成员列表
 */
const getAllMemberList: (
  workspace_id: string | null,
  loading?: Ref<boolean>,
) => Promise<Result<any[]>> = (workspace_id, loading) => {
  return get(`${prefix}/${workspace_id}/user_list`, undefined, loading)
}

/**
 * 新建工作空间成员
 */
const CreateWorkspaceMember: (
  workspace_id: string,
  data: CreateWorkspaceMemberParamsItem[],
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, data, loading) => {
  return post(`${prefix}/${workspace_id}/add_member`, data, undefined, loading)
}

/**
 * 删除工作空间成员
 */
const deleteWorkspaceMember: (
  workspace_id: string,
  user_relation_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, user_relation_id, loading) => {
  return post(`${prefix}/${workspace_id}/remove_member/${user_relation_id}`, undefined, {}, loading)
}

/**
 * 获取添加成员时的角色下拉列表
 */
const getWorkspaceRoleList: (loading?: Ref<boolean>) => Promise<Result<Record<string, any>[]>> = (
  loading,
) => {
  return get('/role_list/current_user', undefined, loading)
}

export default {
  getWorkspaceList,
  getSystemWorkspaceList,
  getWorkspaceMemberList,
  getAllMemberList,
  CreateWorkspaceMember,
  deleteWorkspaceMember,
  getWorkspaceRoleList,
  getWorkspaceListByUser,
}
