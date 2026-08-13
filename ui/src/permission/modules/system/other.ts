/** 系统「其他/关于」类按钮权限 → $perm.other.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  about: () => canSys(P.ABOUT_READ),
  license: () => canSys(P.LICENSE_UPDATE),
  changePassword: () => canSys(P.CHANGE_PASSWORD),
  systemApiKey: () => canSys(P.SYSTEM_API_KEY_EDIT),
  portal: () => canSys(P.PORTAL),
}
