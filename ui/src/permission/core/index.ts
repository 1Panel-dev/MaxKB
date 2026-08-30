import { Role, RoleConstants, Compare, Permission, AggregatePermission, type PermissionContext, type PermissionFactory, type RoleFactory } from './common'
import { useStore } from '@/stores'
import { getWorkspaceId } from '@/utils/resource-context'

export type PermissionInput = Role | string | Permission | PermissionFactory | RoleFactory | AggregatePermission

/** 判断单个权限项，对应 run 的 hasPermissionChild。 */
const hasPermissionChild = (permission: PermissionInput, ctx?: PermissionContext): boolean => {
  const { user } = useStore()
  // Store 初始化或热更新切换期间 Getter 可能短暂不可用，按空权限处理。
  const roles = user.roleSet ?? new Set<string>()
  const permissions = user.permissionMap ?? new Map<string, bigint>()

  if (!permission) {
    return true
  }
  // 工厂：先结合上下文求值出具体 Permission / Role
  if (typeof permission === 'function') {
    permission = permission(ctx)
  }
  // 角色
  if (permission instanceof Role) {
    return roles.has(permission.toString())
  }
  // 组合权限
  if (permission instanceof AggregatePermission) {
    return permission.hasPermission(roles, permissions, ctx)
  }
  // 单条权限
  if (permission instanceof Permission) {
    const p = permission.withContext(ctx)
    const raw = permissions.get(p.toPermissionKey())
    return raw != null && (raw & p.bit()) !== 0n
  }
  // 兜底：直接把字符串当作已就绪的权限/角色 key 命中判断
  if (typeof permission === 'string') {
    return roles.has(permission) || permissions.has(permission)
  }
  return false
}

/**
 * 判断当前用户是否具备给定权限。
 * @param permission 单项或数组（数组时按 compare 组合）
 * @param compare 数组语义：OR = 命中其一即可，AND = 需全部命中，默认 OR
 * @param ctx 资源级/工作空间级权限所需上下文（workspaceId / resourceId）
 */
export const hasPermission = (permission: PermissionInput | PermissionInput[], compare: Compare = Compare.OR, ctx?: PermissionContext): boolean => {
  if (Array.isArray(permission)) {
    return compare === Compare.OR ? permission.some((item) => hasPermissionChild(item, ctx)) : permission.every((item) => hasPermissionChild(item, ctx))
  }
  return hasPermissionChild(permission, ctx)
}

/**
 * 工作空间维度基础权限：命中权限位 / 系统管理员 / 该空间管理员 即可。
 * @param workspaceId 默认取当前路由的 workspaceId。
 */
export const buildBasePermission = (permission: Permission, workspaceId: string | undefined = getWorkspaceId()): AggregatePermission =>
  AggregatePermission.builder()
    .addPermission(permission.newWorkspacePermission(workspaceId))
    .addRole(RoleConstants.ADMIN)
    .addRole(new Role(RoleConstants.WORKSPACE_MANAGE.name, workspaceId))
    .compare(Compare.OR)
    .build()

/**
 * 资源级基础权限：命中资源权限位 / 系统管理员 / 该空间管理员 即可。
 * resourceId 为 'root' 时退化为工作空间维度。
 * @param workspaceId 默认取当前路由的 workspaceId。
 */
export const buildBaseResourcePermission = (permission: Permission, resourceId: string, workspaceId: string | undefined = getWorkspaceId()): AggregatePermission =>
  resourceId === 'root'
    ? buildBasePermission(permission, workspaceId)
    : AggregatePermission.builder()
        .addPermission(permission.newResourcePermission(workspaceId, resourceId))
        .addRole(RoleConstants.ADMIN)
        .addRole(new Role(RoleConstants.WORKSPACE_MANAGE.name, workspaceId))
        .compare(Compare.OR)
        .build()

export { Role, RoleConstants, Compare } from './common'
export { PermissionConstants } from './data'
