/** 系统「对话用户认证」按钮权限。$perm.chatAuth.* */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
    /**
   * 系统「对话用户认证」只读权限
   */
  read: () => canSys(P.CHAT_USER_AUTH_READ) && hasEdition(Edition.PE),
  /**
   * 系统「对话用户认证」编辑权限
   */
  edit: () => canSys(P.CHAT_USER_AUTH_EDIT)
 }
