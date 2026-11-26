import type { RoleInfo } from '@/api/types'
import { ROLE_TYPE } from '@/api/enums'
import { t } from '@/locales'

interface RoleDisplaySource {
  role_info?: RoleInfo[]
  role_name?: string[]
}

const ROLE_NAME_KEYS: Partial<Record<string, string>> = {
  [ROLE_TYPE.ADMIN]: 'role.types.admin',
  [ROLE_TYPE.WORKSPACE_MANAGE]: 'role.types.workspaceAdmin',
  [ROLE_TYPE.USER]: 'role.types.user',
}

export function localizeRoleName(roleId: string | undefined, roleName: string): string {
  const nameKey = roleId ? ROLE_NAME_KEYS[roleId] : undefined
  return nameKey ? t(nameKey) : roleName
}

export function localizeRoleInfo(roleInfo?: RoleInfo[]): RoleInfo[] | undefined {
  return roleInfo?.map((role) => ({
    ...role,
    role_name: localizeRoleName(role.role_id, role.role_name),
  }))
}

export function localizeRoleSource<T extends RoleDisplaySource>(source: T): T {
  const roleInfo = localizeRoleInfo(source.role_info)
  if (!roleInfo) {
    return source
  }
  return {
    ...source,
    role_info: roleInfo,
    role_name: roleInfo.map(({ role_name }) => role_name),
  }
}
