/** 系统「模型资源管理」按钮权限（系统 > 资源管理 > 模型）。全局判定，无 id。 */

import { canSys } from '../../policy'
import { PermissionConstants as P,hasEdition} from '../../core'
import { Edition } from '@/permission/core/common'

const system = {
  // —— 系统页不提供 ——
  create: () => false,
  debug: () => false,
  authToWorkspace: () => false,
  folderRead: () => false,
  folderCreate: () => false,
  folderEdit: () => false,
  folderDelete: () => false,
  folderAuth: () => false,
  folderManage: () => false,

  /**
   * 系统「模型资源管理」（系统 > 资源管理 > 模型）只读权限
   * */
  read: () => canSys(P.RESOURCE_MODEL_READ) && hasEdition(Edition.EE),
  isShare: () => canSys(P.MODEL_READ),

  // —— 模型资源 ——
  /**
   * 系统「模型资源管理」（系统 > 资源管理 > 模型）编辑权限
   * */
  modify: () => canSys(P.RESOURCE_MODEL_EDIT),
  /**
   * 系统「模型资源管理」（系统 > 资源管理 > 模型）模型参数设置权限
   * */
  paramSetting: () => canSys(P.RESOURCE_MODEL_EDIT),
  /**
   * 系统「模型资源管理」（系统 > 资源管理 > 模型）删除权限
   * */
  delete: () => canSys(P.RESOURCE_MODEL_DELETE),
  /**
   * 系统「模型资源管理」（系统 > 资源管理 > 模型）资源授权权限
   * */
  auth: () => canSys(P.RESOURCE_MODEL_AUTH),
  /**
   * 系统「模型资源管理」（系统 > 资源管理 > 模型）查看关联资源权限
   * */
  relateMap: () => canSys(P.RESOURCE_MODEL_RELATE_RESOURCE_VIEW),
}

export default system
