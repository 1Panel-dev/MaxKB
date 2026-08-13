/** 系统「共享模型」按钮权限（系统 > 共享 > 模型）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

const share = {
  // —— 共享页不提供 ——
  isShare: () => false,
  jumpRead: () => false,
  debug: () => false,
  auth: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  // —— 模型资源 ——
  create: () => canSys(P.SHARED_MODEL_CREATE),
  modify: () => canSys(P.SHARED_MODEL_EDIT),
  paramSetting: () => canSys(P.SHARED_MODEL_EDIT),
  delete: () => canSys(P.SHARED_MODEL_DELETE),
  relateMap: () => canSys(P.SHARED_MODEL_RELATE_RESOURCE_VIEW),
  authToWorkspace: () => canSys(P.SHARED_MODEL_TO_WORKSPACE),
}

export default share
