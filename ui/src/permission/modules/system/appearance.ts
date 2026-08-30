/** 系统「外观设置」按钮权限。$perm.appearance.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default { read: () => canSys(P.APPEARANCE_SETTINGS_READ), edit: () => canSys(P.APPEARANCE_SETTINGS_EDIT) }
