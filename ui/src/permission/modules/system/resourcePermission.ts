/** 系统「授权管理」（资源权限）按钮权限 → $perm.resourcePermission.* */

import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  applicationRead: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.APPLICATION_READ],Compare.OR),
  applicationEdit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.APPLICATION_EDIT],Compare.OR),
  knowledgeRead: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.KNOWLEDGE_READ],Compare.OR),
  knowledgeEdit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.KNOWLEDGE_EDIT],Compare.OR),
  toolRead: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.TOOL_READ],Compare.OR),
  toolEdit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.TOOL_EDIT],Compare.OR),
  modelRead: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.MODEL_READ],Compare.OR),
  modelEdit: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.MODEL_EDIT],Compare.OR),
}
