import { RoleTypeEnum } from '@/enums/system'
import { t } from '@/locales'

export const roleTypeMap: Record<RoleTypeEnum, string> = {
  [RoleTypeEnum.ADMIN]: t('views.role.systemAdmin'),
  [RoleTypeEnum.USER]: t('views.role.user'),
  [RoleTypeEnum.WORKSPACE_MANAGE]: t('views.role.workspaceAdmin')
}