import { get, post, del } from '@/request/index'
import type { Ref } from 'vue'
import { Result } from '@/request/Result'
import type { RoleItem, RolePermissionItem, CreateOrUpdateParams } from '@/api/type/role'
import { RoleTypeEnum } from '@/enums/system'

const prefix = '/system/role'
/**
 * 获取角色列表
 */
const getRoleList: (loading?: Ref<boolean>) => Promise<Result<{ internal_role: RoleItem[], custom_role: RoleItem[] }>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 根据类型获取角色权限模版列表
 */
const getRoleTemplate: (role_type: RoleTypeEnum, loading?: Ref<boolean>) => Promise<Result<RolePermissionItem[]>> = (role_type, loading) => {
  return get(`${prefix}/template/${role_type}`, undefined, loading)
}

/**
 * 获取角色权限选中
 */
const getRolePermissionList: (role_id: string, loading?: Ref<boolean>) => Promise<Result<RolePermissionItem[]>> = (role_id, loading) => {
  return get(`${prefix}/${role_id}/permission`, undefined, loading)
}

/**
 * 新建或更新角色
 */
const CreateOrUpdateRole: (
  data: CreateOrUpdateParams,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 删除角色
 */
const deleteRole: (role_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  role_id,
  loading,
) => {
  return del(`${prefix}/${role_id}`, undefined, {}, loading)
}

/**
 * 保存角色权限
 */
const saveRolePermission: (
  role_id: string,
  data: { id: string, enable: boolean }[],
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (role_id, data, loading) => {
  return post(`${prefix}/${role_id}/permission`, data, undefined, loading)
}

export default {
  getRoleList,
  getRolePermissionList,
  getRoleTemplate,
  CreateOrUpdateRole,
  deleteRole,
  saveRolePermission
}