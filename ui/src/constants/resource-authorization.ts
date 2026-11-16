import { RESOURCE_PERMISSION } from '@/api/enums'
import type { OptionItem, ResourcePermission } from '@/api/types'

/** 资源授权页面与抽屉共用的权限展示选项，版本和根目录限制由调用方筛选。 */
export const RESOURCE_PERMISSION_OPTIONS: (OptionItem<ResourcePermission> & { description: string })[] = [
  { description: '', label: 'components.resourceAuthorization.permissions.none.label', value: RESOURCE_PERMISSION.NOT_AUTH },
  {
    description: 'components.resourceAuthorization.permissions.view.description',
    label: 'components.resourceAuthorization.permissions.view.label',
    value: RESOURCE_PERMISSION.VIEW,
  },
  {
    description: 'components.resourceAuthorization.permissions.manage.description',
    label: 'components.resourceAuthorization.permissions.manage.label',
    value: RESOURCE_PERMISSION.MANAGE,
  },
  {
    description: 'components.resourceAuthorization.permissions.role.description',
    label: 'components.resourceAuthorization.permissions.role.label',
    value: RESOURCE_PERMISSION.ROLE,
  },
]
