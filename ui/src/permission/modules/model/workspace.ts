/** 工作空间「模型」按钮权限。（模型无独立文件夹资源权限，文件夹操作复用模型级权限）*/

import { can, canRes } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 工作空间级 ——
  isShare: () => can(P.MODEL_READ),
  /**
   * 工作空间「模型」创建权限
   */
  create: () => can(P.MODEL_CREATE),
  debug: () => false,
  authToWorkspace: () => false,

  // —— 文件夹（复用模型级权限）——
  folderRead: () => true,
  folderManage: () => true,
  folderAuth: () => false,
  folderCreate: () => can(P.MODEL_CREATE),
  folderEdit: () => can(P.MODEL_EDIT),
  folderDelete: () => can(P.MODEL_DELETE),

  // —— 模型资源级 ——
  /**
   * 工作空间「模型」编辑权限
   */
  modify: (id: string) => canRes(P.MODEL_EDIT, id),
  /**
   * 工作空间「模型」模型参数设置权限
   */
  paramSetting: (id: string) => canRes(P.MODEL_EDIT, id),
  /**
   * 工作空间「模型」删除权限
   */
  delete: (id: string) => canRes(P.MODEL_DELETE, id),
  /**
   * 工作空间「模型」资源授权权限
   */
  auth: (id: string) => canRes(P.MODEL_RESOURCE_AUTHORIZATION, id),
  /**
   * 工作空间「模型」查看关联资源权限
   */
  relateMap: (id: string) => canRes(P.MODEL_RELATE_RESOURCE_VIEW, id),
}

export default workspace
