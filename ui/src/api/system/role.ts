import { get, post, del } from '@/request/index'
import type { Result } from '@/request/Result'
import type { Ref } from 'vue'

const prefix = '/system/role'

const getRoleList = (loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`${prefix}`, undefined, loading)
}

/** 根据角色类型获取权限模板 */
const getRoleTemplate = (role_type: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`${prefix}/template/${role_type}`, undefined, loading)
}

const getRolePermissionList = (role_id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`${prefix}/${role_id}/permission`, undefined, loading)
}

const CreateOrUpdateRole = (
  data: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return post(`${prefix}`, data, undefined, loading)
}

const deleteRole = (role_id: string, loading?: Ref<boolean>): Promise<Result<boolean>> => {
  return del(`${prefix}/${role_id}`, loading)
}

const saveRolePermission = (
  role_id: string,
  data: { id: string; enable: boolean }[],
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return post(`${prefix}/${role_id}/permission`, data, undefined, loading)
}

const getRoleMemberList = (
  role_id: string,
  page: { current_page: number; page_size: number },
  param: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(
    `${prefix}/${role_id}/user_list/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

const CreateMember = (
  role_id: string,
  data: { members: any[] },
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return post(`${prefix}/${role_id}/add_member`, data, undefined, loading)
}

const deleteRoleMember = (
  role_id: string,
  user_relation_id: string,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return del(`${prefix}/${role_id}/remove_member/${user_relation_id}`, loading)
}

const getUserPermissions = (loading?: Ref<boolean>): Promise<Result<any>> => {
  return get('/user/permissions', undefined, loading)
}

export default {
  getUserPermissions,
  getRoleList,
  getRoleTemplate,
  getRolePermissionList,
  CreateOrUpdateRole,
  deleteRole,
  saveRolePermission,
  getRoleMemberList,
  CreateMember,
  deleteRoleMember,
}
