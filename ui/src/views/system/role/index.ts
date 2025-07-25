import {RoleTypeEnum} from '@/enums/system'
import {t} from '@/locales'
import useStore from '@/stores'
import {computed} from "vue";

const {user} = useStore()
export const roleTypeMap = computed(() => ({
  ...(user.is_admin()
    ? {
      [RoleTypeEnum.ADMIN]: t('views.role.systemAdmin'),
    }
    : {}),
  [RoleTypeEnum.USER]: t('views.role.user'),
  [RoleTypeEnum.WORKSPACE_MANAGE]: t('views.role.workspaceAdmin'),
}))
