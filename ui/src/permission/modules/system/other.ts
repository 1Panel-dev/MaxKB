/** 系统「其他/关于」类按钮权限 → $perm.other.* */

import { canSys } from '../../policy'
import { PermissionConstants as P, hasPermission, RoleConstants, Compare} from '../../core'

export default {
  /**
   * 系统「其他/关于」关于权限
   */
  about: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.ABOUT_READ],Compare.OR),
  /**
   * 系统「其他/关于」切换语言权限
   */
  SWITCH_LANGUAGE: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SWITCH_LANGUAGE],Compare.OR),
  /**
   * 系统「其他/关于」更新许可证权限
   */
  license: () => canSys(P.LICENSE_UPDATE),
  /**
   * 系统「其他/关于」修改密码权限
   */
  changePassword: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.CHANGE_PASSWORD],Compare.OR),
  /**
   * 系统「其他/关于」系统APIKey权限
   */
  systemApiKey: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.SYSTEM_API_KEY_EDIT],Compare.OR),
  /**
   * 系统「其他/关于」门户权限
   */
  portal: () => hasPermission([RoleConstants.ADMIN,RoleConstants.WORKSPACE_MANAGE,P.PORTAL],Compare.OR),
}
