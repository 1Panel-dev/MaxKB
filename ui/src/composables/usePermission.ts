import { useUserStore } from '@/stores/user'
import { permissionMap, type ResourceType } from '@/permission'

/**
 * 检查用户是否拥有指定权限 ID。
 * 权限数据来自 userStore.userInfo.permissions（profile 接口返回的字段）。
 * 支持三种匹配模式：
 * 1. 精确匹配: permissions 包含 "SYSTEM_RESOURCE_APPLICATION:READ+EDIT"
 * 2. 前缀匹配: permissions 包含 "SYSTEM_RESOURCE_APPLICATION:READ+EDIT:..."
 * 3. 资源路径格式: permissions 包含 "APPLICATION:READ+EDIT:/WORKSPACE/..."
 */
export function hasPerm(permId: string): boolean {
  const userStore = useUserStore()
  const perms = (userStore.userInfo as any)?.permissions
  if (!Array.isArray(perms)) return false
  // 精确匹配
  if (perms.includes(permId)) return true
  // 前缀匹配（带资源路径的格式）
  const prefix = permId + ':'
  return perms.some((p: string) => p.startsWith(prefix))
}

/**
 * 检查用户是否拥有某个资源类型的特定操作权限
 */
export function hasResourcePerm(resource: ResourceType, action: string): boolean {
  const userStore = useUserStore()
  const perms = (userStore.userInfo as any)?.permissions
  if (!Array.isArray(perms)) return false

  const resourcePerms = permissionMap[resource] as Record<string, string[]> | undefined
  if (!resourcePerms) return false
  const requiredIds = resourcePerms[action]
  if (!requiredIds?.length) return false

  // Check each required ID with exact + prefix match
  for (const id of requiredIds) {
    if (perms.includes(id)) return true
    if (perms.some((p: string) => p.startsWith(id + ':'))) return true
  }
  return false
}

/** 遗留的兼容导出 */
export async function loadUserPermissions(_force?: boolean) {}
export function resetPermissions() {}
