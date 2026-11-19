import type { ResourcePermission } from '@/api/types'
import { RESOURCE_PERMISSION } from '@/api/enums'

/** 资源授权页面与抽屉共用的权限展示选项，版本和根目录限制由调用方筛选。 */
export const RESOURCE_PERMISSION_OPTIONS: { labelKey: string; descriptionKey?: string; value: ResourcePermission }[] = [
  { labelKey: 'authorization.permission.notAuthorized.label', value: RESOURCE_PERMISSION.NOT_AUTH },
  { labelKey: 'authorization.permission.view.label', descriptionKey: 'authorization.permission.view.description', value: RESOURCE_PERMISSION.VIEW },
  {
    labelKey: 'authorization.permission.manage.label',
    descriptionKey: 'authorization.permission.manage.description',
    value: RESOURCE_PERMISSION.MANAGE,
  },
  { labelKey: 'authorization.permission.role.label', descriptionKey: 'authorization.permission.role.description', value: RESOURCE_PERMISSION.ROLE },
]
