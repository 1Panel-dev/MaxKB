/** 系统「外观设置」按钮权限。$perm.appearance.* */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「外观设置」只读权限
   */
  read: () => canSys(P.APPEARANCE_SETTINGS_READ) && hasEdition(Edition.PE),
  edit: () => canSys(P.APPEARANCE_SETTINGS_EDIT)
 }
