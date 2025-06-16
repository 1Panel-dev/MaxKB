import useStore from '@/stores'
import { Role, Permission, ComplexPermission } from '@/utils/permission/type'
import { isFunction } from '@/utils/common'

type PF = () => Role | string | Permission | ComplexPermission
/**
 * 是否包含当前权限
 * @param permission 当前权限
 * @returns  True 包含 false 不包含
 */
const hasPermissionChild = (permission: Role | string | Permission | ComplexPermission | PF) => {
  const { user } = useStore()
  const permissions = user.getPermissions()
  const role: Array<string> = user.getRole()
  if (!permission) {
    return true
  }

  if (isFunction(permission)) {
    permission = (permission as PF)()
  }
  if (permission instanceof Role) {
    return role.includes(permission.role)
  }
  if (permission instanceof Permission) {
    return permissions.includes(permission.permission)
  }
  if (permission instanceof ComplexPermission) {
    const permissionOk = permission.permissionList.some((p) => permissions.includes(p))
    const roleOk = role.some((r) => permission.roleList.includes(r))
    return permission.compare === 'AND' ? permissionOk && roleOk : permissionOk || roleOk
  }
  if (typeof permission === 'string') {
    return permissions.includes(permission)
  }

  return false
}
/**
 * 判断是否有角色和权限
 * @param role         角色
 * @param permissions  权限
 * @param requiredPermissions  权限
 * @returns
 */
export const hasPermission = (
  permission:
    | Array<Role | string | Permission | ComplexPermission | PF>
    | Role
    | string
    | Permission
    | ComplexPermission
    | PF,
  compare: 'OR' | 'AND',
): boolean => {
  if (permission instanceof Array) {
    return compare === 'OR'
      ? permission.some((p) => hasPermissionChild(p))
      : permission.every((p) => hasPermissionChild(p))
  } else {
    return hasPermissionChild(permission)
  }
}
