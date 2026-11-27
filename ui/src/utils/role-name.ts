/** 统一内置角色的界面展示名称。 */
import type { RoleType } from '@/api/types'
import { ROLE_TYPE_LABELS } from '@/constants/auth'

/** 按固定 ID 读取内置角色译名，自定义角色沿用接口名称。 */
export function getRoleName(roleId: string | undefined, roleName: string): string {
  if (roleId && Object.hasOwn(ROLE_TYPE_LABELS, roleId)) {
    return ROLE_TYPE_LABELS[roleId as RoleType]
  }
  return roleName
}
