/** 系统「授权管理」（资源权限）按钮权限 → $perm.resourcePermission.* */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  applicationRead: () => canSys(P.APPLICATION_RESOURCE_PERMISSION_READ),
  applicationEdit: () => canSys(P.APPLICATION_RESOURCE_PERMISSION_EDIT),
  knowledgeRead: () => canSys(P.KNOWLEDGE_RESOURCE_PERMISSION_READ),
  knowledgeEdit: () => canSys(P.KNOWLEDGE_RESOURCE_PERMISSION_EDIT),
  toolRead: () => canSys(P.TOOL_RESOURCE_PERMISSION_READ),
  toolEdit: () => canSys(P.TOOL_RESOURCE_PERMISSION_EDIT),
  modelRead: () => canSys(P.MODEL_RESOURCE_PERMISSION_READ),
  modelEdit: () => canSys(P.MODEL_RESOURCE_PERMISSION_EDIT),
}
