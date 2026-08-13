/** 系统「对话用户」按钮权限。$perm.chatUser.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  read: () => canSys(P.CHAT_USER_READ),
  create: () => canSys(P.CHAT_USER_CREATE),
  sync: () => canSys(P.CHAT_USER_SYNC),
  edit: () => canSys(P.CHAT_USER_EDIT),
  delete: () => canSys(P.CHAT_USER_DELETE),
  userGroup: () => canSys(P.CHAT_USER_GROUP),
  quotaSetting: () => canSys(P.CHAT_USER_QUOTA_SETTING),
}
