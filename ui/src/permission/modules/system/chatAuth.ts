/** 系统「对话用户认证」按钮权限。$perm.chatAuth.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default { edit: () => canSys(P.CHAT_USER_AUTH_EDIT) }
