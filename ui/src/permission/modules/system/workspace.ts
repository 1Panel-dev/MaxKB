/** 系统「工作空间」实体管理按钮权限。$perm.workspace.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「工作空间」只读权限
   * */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.WORKSPACE_READ],Compare.OR) && hasEdition(Edition.PE),
  /**
   * 系统「工作空间」创建权限
   */
  create: () => canSys(P.WORKSPACE_CREATE),
  /**
   * 系统「工作空间」编辑权限
   */
  edit: () => canSys(P.WORKSPACE_EDIT),
  /**
   * 系统「工作空间」删除权限
   */
  delete: () => canSys(P.WORKSPACE_DELETE),
  /**
   * 系统「工作空间」添加成员权限
   */
  addMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.WORKSPACE_ADD_MEMBER],Compare.OR),
  /**
   * 系统「工作空间」移除成员权限
   */
  removeMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.WORKSPACE_REMOVE_MEMBER],Compare.OR),
}
