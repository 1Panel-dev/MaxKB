/** 系统「对话用户」按钮权限。$perm.chatUser.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  /**
   * 系统「对话用户」只读权限
   */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_READ],Compare.OR),
  create: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_CREATE],Compare.OR),
  sync: () => canSys(P.CHAT_USER_SYNC),
  edit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_EDIT],Compare.OR),
  delete: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_DELETE],Compare.OR),
  userGroup: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_GROUP],Compare.OR),
  quotaSetting: () => canSys(P.CHAT_USER_QUOTA_SETTING),
}
