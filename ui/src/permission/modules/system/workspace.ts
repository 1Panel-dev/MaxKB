/** 系统「工作空间」实体管理按钮权限。$perm.workspace.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

export default {
  /**
   * 系统「工作空间」只读权限
   * */
  read: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.WORKSPACE_READ],Compare.OR) && hasEdition(Edition.PE),
  create: () => canSys(P.WORKSPACE_CREATE),
  edit: () => canSys(P.WORKSPACE_EDIT),
  delete: () => canSys(P.WORKSPACE_DELETE),
  addMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.WORKSPACE_ADD_MEMBER],Compare.OR),
  removeMember: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.WORKSPACE_REMOVE_MEMBER],Compare.OR),
}
