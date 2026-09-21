/** 系统「对话用户」按钮权限。$perm.chatUser.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  /**
   * 系统「对话用户」只读权限
   */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_READ],Compare.OR),
    /**
   * 系统「对话用户」创建权限
   */
  create: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_CREATE],Compare.OR),
    /**
   * 系统「对话用户」同步权限
   */
  sync: () => canSys(P.CHAT_USER_SYNC),
    /**
   * 系统「对话用户」编辑权限
   */
  edit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_EDIT],Compare.OR),
    /**
   * 系统「对话用户」删除权限
   */
  delete: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_DELETE],Compare.OR),
    /**
   * 系统「对话用户」设置用户组权限
   */
  userGroup: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHAT_USER_GROUP],Compare.OR),
    /**
   * 系统「对话用户」配额设置权限
   */
  quotaSetting: () => canSys(P.CHAT_USER_QUOTA_SETTING),
}
