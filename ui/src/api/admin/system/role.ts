import { del, get, post } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type {
  CreateRoleMembersRequest,
  RequestParams,
  RoleItem,
  RoleMember,
  RolePermissionModule,
  RolePayload,
  SaveRolePermissionRequest,
} from '@/api/types'

const prefix = '/system/role'

/** 获取内置角色与自定义角色列表。 */
const getRoleList = () => {
  return get<{ internal_role: RoleItem[]; custom_role: RoleItem[] }>(prefix)
}

/** 创建或重命名自定义角色。 */
const postRole = (payload: RolePayload) => {
  return post<RolePayload, RoleItem>(prefix, payload)
}

/** 删除自定义角色。 */
const deleteRole = (roleId: string) => {
  return del<boolean>(`${prefix}/${roleId}`)
}


/** 获取指定角色的权限配置。 */
const getRolePermissionList = (roleId: string) => {
  return get<RolePermissionModule[]>(`${prefix}/${roleId}/permission`)
}


/** 保存指定角色的权限配置。 */
const postRolePermissions = (roleId: string, permissions: SaveRolePermissionRequest[]) => {
  return post<SaveRolePermissionRequest[], boolean>(`${prefix}/${roleId}/permission`, permissions)
}

/** 获取指定角色的成员分页列表。 */
const getRoleMemberList = (roleId: string, page: ParamsPage, query?: RequestParams) => {
  return get<ResponsePage<RoleMember>>(
    `${prefix}/${roleId}/user_list/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 为指定角色添加成员。 */
const postRoleMembers = (roleId: string, payload: CreateRoleMembersRequest) => {
  return post<CreateRoleMembersRequest, boolean>(`${prefix}/${roleId}/add_member`, payload)
}

/** 从指定角色移除成员。 */
const deleteRoleMember = (roleId: string, userRelationId: string) => {
  return del<boolean>(`${prefix}/${roleId}/remove_member/${userRelationId}`)
}

export default {
  deleteRole,
  deleteRoleMember,
  getRoleList,
  getRoleMemberList,
  getRolePermissionList,
  postRole,
  postRoleMembers,
  postRolePermissions,
}
