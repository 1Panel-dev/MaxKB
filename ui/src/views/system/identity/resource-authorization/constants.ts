import type { OptionItem, ResourceAuthorizationType, ResourcePermission } from '@/api/types'
import { RESOURCE_PERMISSION, RESOURCE_TYPE } from '@/api/enums'
import { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'
import { useStore } from '@/stores'
const { auth } = useStore()

export const RESOURCE_AUTHORIZATION_LABELS: Record<ResourceAuthorizationType, string> = {
  [RESOURCE_TYPE.APPLICATION]: '智能体',
  [RESOURCE_TYPE.KNOWLEDGE]: '知识库',
  [RESOURCE_TYPE.MODEL]: '模型',
  [RESOURCE_TYPE.TOOL]: '工具',
}

interface PermissionOption extends OptionItem<ResourcePermission> {
  description: string
}

export function getPermissionOptions(): PermissionOption[] {
  const permissionOptions = RESOURCE_PERMISSION_OPTIONS
  if (auth.isCE) {
    return permissionOptions.filter((item) => item.value !== RESOURCE_PERMISSION.ROLE)
  }

  return permissionOptions
}
