/** 系统「其他/关于」类按钮权限 → $perm.other.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  about: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ABOUT_READ],Compare.OR),
  SWITCH_LANGUAGE: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SWITCH_LANGUAGE],Compare.OR),
  license: () => canSys(P.LICENSE_UPDATE),
  changePassword: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHANGE_PASSWORD],Compare.OR),
  systemApiKey: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_API_KEY_EDIT],Compare.OR),
  portal: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.PORTAL],Compare.OR),
}
