import {RoleTypeEnum} from '@/enums/system'
import {t} from '@/locales'
import useStore from '@/stores'

const {user} = useStore()
export const roleTypeMap: Record<RoleTypeEnum, string> = {
  ...(user.is_admin()
    ? {
      [RoleTypeEnum.ADMIN]: t('views.role.systemAdmin'),
    }
    : {}),
  [RoleTypeEnum.USER]: t('views.role.user'),
  [RoleTypeEnum.WORKSPACE_MANAGE]: t('views.role.workspaceAdmin'),
};
