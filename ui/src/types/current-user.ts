/** 当前登录用户使用的数据类型。 */

import type { WorkspaceItem } from './workspace'

export interface CurrentUser {
  email: string
  id: string
  is_edit_password?: boolean
  language?: string
  nick_name: string
  permissions: string[]
  role: string[]
  role_name?: string[]
  source?: string
  username: string
  workspace_list?: WorkspaceItem[]
}
