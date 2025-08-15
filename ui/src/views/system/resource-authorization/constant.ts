import { AuthorizationEnum } from '@/enums/system'
import { t } from '@/locales'

export const permissionOptions = [
  {
    label: t('views.system.resourceAuthorization.setting.notAuthorized'),
    value: AuthorizationEnum.NOT_AUTH,
    desc: '',
  },
  {
    label: t('views.system.resourceAuthorization.setting.check'),
    value: AuthorizationEnum.VIEW,
    desc: t('views.system.resourceAuthorization.setting.checkDesc'),
  },
  {
    label: t('views.system.resourceAuthorization.setting.management'),
    value: AuthorizationEnum.MANAGE,
    desc: t('views.system.resourceAuthorization.setting.managementDesc'),
  },
  {
    label: t('views.system.resourceAuthorization.setting.role'),
    value: AuthorizationEnum.ROLE,
    desc: t('views.system.resourceAuthorization.setting.roleDesc'),
  },
]
