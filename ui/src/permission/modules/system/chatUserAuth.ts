/** 系统「访客认证设置」按钮权限 → $perm.chatUserAuth.* */

import { PermissionConstants as P } from '../../core'
import { canSys } from '../../policy'

export default { edit: () => canSys(P.CHAT_USER_AUTH_EDIT) }
