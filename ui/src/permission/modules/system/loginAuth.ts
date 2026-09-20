/** 系统「用户认证」按钮权限。$perm.loginAuth.* */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「用户认证」只读权限
   */
  read: () => canSys(P.LOGIN_AUTH_READ) && hasEdition(Edition.PE),
  edit: () => canSys(P.LOGIN_AUTH_EDIT)
 }
