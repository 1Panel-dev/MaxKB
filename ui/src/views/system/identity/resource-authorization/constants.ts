import { computed, reactive } from 'vue'
import type { ResourceAuthorizationType } from '@/api/types'
import { RESOURCE_PERMISSION, RESOURCE_TYPE } from '@/api/enums'
import { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'
import { t } from '@/locales'
import { useStore } from '@/stores'
const { auth } = useStore()

export const RESOURCE_AUTHORIZATION_LABELS: Record<ResourceAuthorizationType, string> = reactive({
  [RESOURCE_TYPE.APPLICATION]: computed(() => t('application.title')),
  [RESOURCE_TYPE.KNOWLEDGE]: computed(() => t('knowledge.title')),
  [RESOURCE_TYPE.MODEL]: computed(() => t('model.title')),
  [RESOURCE_TYPE.TOOL]: computed(() => t('tool.title')),
})

export function getPermissionOptions(): (typeof RESOURCE_PERMISSION_OPTIONS)[number][] {
  const permissionOptions = RESOURCE_PERMISSION_OPTIONS
  if (auth.isCE) {
    return permissionOptions.filter((item) => item.value !== RESOURCE_PERMISSION.ROLE)
  }

  return permissionOptions
}
