/** 系统「资源授权」按钮权限（按资源类型分组）。$perm.authorization.application.read() ... */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  application: { read: () => canSys(P.APPLICATION_RESOURCE_PERMISSION_READ), edit: () => canSys(P.APPLICATION_RESOURCE_PERMISSION_EDIT) },
  knowledge: { read: () => canSys(P.KNOWLEDGE_RESOURCE_PERMISSION_READ), edit: () => canSys(P.KNOWLEDGE_RESOURCE_PERMISSION_EDIT) },
  tool: { read: () => canSys(P.TOOL_RESOURCE_PERMISSION_READ), edit: () => canSys(P.TOOL_RESOURCE_PERMISSION_EDIT) },
  model: { read: () => canSys(P.MODEL_RESOURCE_PERMISSION_READ), edit: () => canSys(P.MODEL_RESOURCE_PERMISSION_EDIT) },
}
