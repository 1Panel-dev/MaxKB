/** 工作空间「模型」按钮权限。（模型无独立文件夹资源权限，文件夹操作复用模型级权限）*/

import { can, canRes } from '../../policy'
import { PermissionConstants as P } from '../../core'

const workspace = {
  // —— 工作空间级 ——
  isShare: () => can(P.MODEL_READ),
  create: () => can(P.MODEL_CREATE),
  jumpRead: () => false,
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
  modify: (id: string) => canRes(P.MODEL_EDIT, id),
  paramSetting: (id: string) => canRes(P.MODEL_EDIT, id),
  delete: (id: string) => canRes(P.MODEL_DELETE, id),
  auth: (id: string) => canRes(P.MODEL_RESOURCE_AUTHORIZATION, id),
  relateMap: (id: string) => canRes(P.MODEL_RELATE_RESOURCE_VIEW, id),
}

export default workspace
