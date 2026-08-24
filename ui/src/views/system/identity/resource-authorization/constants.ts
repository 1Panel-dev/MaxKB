import { RESOURCE_TYPE, RESOURCE_PERMISSION } from '@/api/enums'
import type { OptionItem, ResourceAuthorizationType, ResourcePermission } from '@/api/types'
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
  const permissionOptions: PermissionOption[] = [
    {
      description: '',
      label: '不授权',
      value: RESOURCE_PERMISSION.NOT_AUTH,
    },
    {
      description: '仅能查看和使用该资源',
      label: '查看',
      value: RESOURCE_PERMISSION.VIEW,
    },
    {
      description: '可对该资源进行删改操作',
      label: '管理',
      value: RESOURCE_PERMISSION.MANAGE,
    },
    {
      description: '根据用户角色中的权限授权用户对该资源的操作权限',
      label: '按用户角色',
      value: RESOURCE_PERMISSION.ROLE,
    },
  ]
  if (auth.isCE) {
    return permissionOptions.filter((item) => item.value !== RESOURCE_PERMISSION.ROLE)
  }

  return permissionOptions
}
