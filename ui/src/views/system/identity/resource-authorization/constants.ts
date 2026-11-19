import type { ResourceAuthorizationType } from '@/api/types'
import { RESOURCE_PERMISSION, RESOURCE_TYPE } from '@/api/enums'
import { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'
import { useStore } from '@/stores'
const { auth } = useStore()

export const RESOURCE_AUTHORIZATION_MESSAGE_KEYS: Record<ResourceAuthorizationType, string> = {
  [RESOURCE_TYPE.APPLICATION]: 'application.title',
  [RESOURCE_TYPE.KNOWLEDGE]: 'knowledge.title',
  [RESOURCE_TYPE.MODEL]: 'model.title',
  [RESOURCE_TYPE.TOOL]: 'tool.title',
}

export function getPermissionOptions(): (typeof RESOURCE_PERMISSION_OPTIONS)[number][] {
  const permissionOptions = RESOURCE_PERMISSION_OPTIONS
  if (auth.isCE) {
    return permissionOptions.filter((item) => item.value !== RESOURCE_PERMISSION.ROLE)
  }

  return permissionOptions
}
