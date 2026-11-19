import { computed, reactive } from 'vue'
import type { ResourcePermission } from '@/api/types'
import { RESOURCE_PERMISSION } from '@/api/enums'
import { t } from '@/locales'

/** 资源授权页面与抽屉共用的权限展示选项，版本和根目录限制由调用方筛选。 */
export const RESOURCE_PERMISSION_OPTIONS: { label: string; description?: string; value: ResourcePermission }[] = reactive([
  { label: computed(() => t('authorization.permission.notAuthorized.label')), value: RESOURCE_PERMISSION.NOT_AUTH },
  {
    label: computed(() => t('authorization.permission.view.label')),
    description: computed(() => t('authorization.permission.view.description')),
    value: RESOURCE_PERMISSION.VIEW,
  },
  {
    label: computed(() => t('authorization.permission.manage.label')),
    description: computed(() => t('authorization.permission.manage.description')),
    value: RESOURCE_PERMISSION.MANAGE,
  },
  {
    label: computed(() => t('authorization.permission.role.label')),
    description: computed(() => t('authorization.permission.role.description')),
    value: RESOURCE_PERMISSION.ROLE,
  },
])
