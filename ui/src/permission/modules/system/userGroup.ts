/** 系统「用户组」按钮权限。$perm.userGroup.* */

import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  /**
   * 系统「用户组」只读权限
   * */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_USER_GROUP_READ],Compare.OR),
  /**
   * 系统「用户组」创建权限
   */
  create: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_USER_GROUP_CREATE],Compare.OR),
  /**
   * 系统「用户组」编辑权限
   */
  edit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_USER_GROUP_EDIT],Compare.OR),
  /**
   * 系统「用户组」删除权限
   */
  delete: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_USER_GROUP_DELETE],Compare.OR),
  /**
   * 系统「用户组」添加成员权限
   */
  addMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_USER_GROUP_ADD_MEMBER],Compare.OR),
  /**
   * 系统「用户组」移除成员权限
   */
  removeMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_USER_GROUP_REMOVE_MEMBER],Compare.OR),
}
