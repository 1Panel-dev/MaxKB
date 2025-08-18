import { AuthorizationEnum } from '@/enums/system'
import { t } from '@/locales'
import { hasPermission } from '@/utils/permission'
import { EditionConst } from '@/utils/permission/data'

const notCommunity = hasPermission([EditionConst.IS_EE,EditionConst.IS_PE],'OR')

const permissionOptions = [
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
]

if (notCommunity) {
  permissionOptions.push(
    {
    label: t('views.system.resourceAuthorization.setting.role'),
    value: AuthorizationEnum.ROLE,
    desc: t('views.system.resourceAuthorization.setting.roleDesc'),
  },
  )
}

export {permissionOptions}