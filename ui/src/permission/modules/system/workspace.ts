/** 系统「工作空间」实体管理按钮权限。$perm.workspace.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  read: () => canSys(P.WORKSPACE_READ),
  create: () => canSys(P.WORKSPACE_CREATE),
  edit: () => canSys(P.WORKSPACE_EDIT),
  delete: () => canSys(P.WORKSPACE_DELETE),
  addMember: () => canSys(P.WORKSPACE_ADD_MEMBER),
  removeMember: () => canSys(P.WORKSPACE_REMOVE_MEMBER),
}
