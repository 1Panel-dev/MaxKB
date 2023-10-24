import useStore from '@/stores';
import { Role, Permission, ComplexPermission } from '@/utils/permission/type'
/**
 * 是否包含当前权限
 * @param permission 当前权限
 * @returns  True 包含 false 不包含
 */
const hasPermissionChild = (permission: Role | string | Permission | ComplexPermission) => {
  const { user } = useStore();
  const permissions = user.getPermissions()
  const role = user.getRole()
  if (!permission) {
    return true
  }
  if (permission instanceof Role) {
    return role === permission.role
  }
  if (permission instanceof Permission) {
    return permissions.includes(permission.permission)
  }
  if (permission instanceof ComplexPermission) {
    const permissionOk = permission.permissionList.some((p) => permissions.includes(p))
    const roleOk = permission.roleList.includes(role)
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
    | Array<Role | string | Permission | ComplexPermission>
    | Role
    | string
    | Permission
    | ComplexPermission,
  compare: 'OR' | 'AND'
): boolean => {
  if (permission instanceof Array) {
    return compare === 'OR'
      ? permission.some((p) => hasPermissionChild(p))
      : permission.every((p) => hasPermissionChild(p))
  } else {
    return hasPermissionChild(permission)
  }
}
