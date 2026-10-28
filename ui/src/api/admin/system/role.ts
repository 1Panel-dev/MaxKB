import { del, get, post } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type {
  CreateRoleMembersRequest,
  Dict,
  RoleItem,
  RoleMember,
  RolePayload,
  RolePermissionModule,
  RoleTypeGroup,
  SaveRolePermissionRequest,
} from '@/api/types'

const prefix = '/system/role'

/** 获取按角色类型分组的角色列表。 */
const getRoleList = () => {
  return get<{ internal_role: RoleItem[]; custom_role: RoleItem[] } | RoleTypeGroup[]>(prefix).then((data) => {
    if (Array.isArray(data)) {
      return data
    }
    const roles = [...(data.internal_role ?? []), ...(data.custom_role ?? [])]
    return [...new Set(roles.map((role) => role.type))].map((roleType) => ({
      role_type: roleType,
      role_list: roles.filter((role) => role.type === roleType),
    }))
  })
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
const getRoleMemberList = (roleId: string, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<RoleMember>>(`${prefix}/${roleId}/user_list/${page.currentPage}/${page.pageSize}`, query)
}

/** 为指定角色添加成员。 */
const postRoleMembers = (roleId: string, payload: CreateRoleMembersRequest) => {
  return post<CreateRoleMembersRequest, boolean>(`${prefix}/${roleId}/add_member`, payload)
}

/** 从指定角色移除成员。 */
const deleteRoleMember = (roleId: string, userRelationId: string) => {
  return del<boolean>(`${prefix}/${roleId}/remove_member/${userRelationId}`)
}

/** 从指定角色批量移除成员。 */
const deleteRoleMembers = (roleId: string, userRelationIds: string[]) => {
  return del<{ member_ids: string[] }, boolean>(`${prefix}/${roleId}/remove_member/batch`, undefined, { member_ids: userRelationIds })
}

export default {
  deleteRole,
  deleteRoleMember,
  deleteRoleMembers,
  getRoleList,
  getRoleMemberList,
  getRolePermissionList,
  postRole,
  postRoleMembers,
  postRolePermissions,
}
