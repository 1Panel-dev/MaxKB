/** 系统「用户认证」按钮权限。$perm.loginAuth.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default { read: () => canSys(P.LOGIN_AUTH_READ), edit: () => canSys(P.LOGIN_AUTH_EDIT) }
