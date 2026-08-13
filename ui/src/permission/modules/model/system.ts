/** 系统「模型资源管理」按钮权限（系统 > 资源管理 > 模型）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

const system = {
  // —— 系统页不提供 ——
  create: () => false,
  jumpRead: () => false,
  debug: () => false,
  authToWorkspace: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  isShare: () => canSys(P.MODEL_READ),

  // —— 模型资源 ——
  modify: () => canSys(P.RESOURCE_MODEL_EDIT),
  paramSetting: () => canSys(P.RESOURCE_MODEL_EDIT),
  delete: () => canSys(P.RESOURCE_MODEL_DELETE),
  auth: () => canSys(P.RESOURCE_MODEL_AUTH),
  relateMap: () => canSys(P.RESOURCE_MODEL_RELATE_RESOURCE_VIEW),
}

export default system
