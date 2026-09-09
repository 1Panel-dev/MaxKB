import { RESOURCE_PERMISSION } from '@/api/enums'
import type { OptionItem, ResourcePermission } from '@/api/types'

/** 资源授权页面与抽屉共用的权限展示选项，版本和根目录限制由调用方筛选。 */
export const RESOURCE_PERMISSION_OPTIONS: (OptionItem<ResourcePermission> & { description: string })[] = [
  { description: '', label: '不授权', value: RESOURCE_PERMISSION.NOT_AUTH },
  { description: '仅能查看和使用该资源', label: '查看', value: RESOURCE_PERMISSION.VIEW },
  { description: '可对该资源进行删改操作', label: '管理', value: RESOURCE_PERMISSION.MANAGE },
  { description: '根据用户角色中的权限授权用户对该资源的操作权限', label: '按用户角色', value: RESOURCE_PERMISSION.ROLE },
]
