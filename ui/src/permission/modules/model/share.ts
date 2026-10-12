/** 系统「共享模型」按钮权限（系统 > 共享 > 模型）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

const share = {
  // —— 共享页不提供 ——
  isShare: () => false,
  debug: () => false,
  auth: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  /**
   * 系统「共享模型」（系统 > 共享 > 模型）只读权限
   */
  read: () => canSys(P.SHARED_MODEL_READ) && hasEdition(Edition.EE),

  // —— 模型资源 ——
  /**
   * 系统「共享模型」（系统 > 共享 > 模型） 创建权限
   */
  create: () => canSys(P.SHARED_MODEL_CREATE),
  /**
   * 系统「共享模型」（系统 > 共享 > 模型） 编辑权限
   */
  modify: () => canSys(P.SHARED_MODEL_EDIT),
  /**
   * 系统「共享模型」（系统 > 共享 > 模型）模型参数设置权限
   */
  paramSetting: () => canSys(P.SHARED_MODEL_EDIT),
  /**
   * 系统「共享模型」（系统 > 共享 > 模型）删除权限
   */
  delete: () => canSys(P.SHARED_MODEL_DELETE),
  /**
   * 系统「共享模型」（系统 > 共享 > 模型）查看关联资源权限
   */
  relateMap: () => canSys(P.SHARED_MODEL_RELATE_RESOURCE_VIEW),
  /**
   * 系统「共享模型」（系统 > 共享 > 模型）授权工作空间权限
   */
  authToWorkspace: () => canSys(P.SHARED_MODEL_TO_WORKSPACE),
}

export default share
