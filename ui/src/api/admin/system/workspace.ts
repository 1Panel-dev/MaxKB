import { get } from '../core/request'
import type { ResponsePage, ParamsPage } from '../core/types'
import type { RequestParams, WorkspaceItem } from '@/types'

const prefix = '/system/workspace'

/** 首页头部工作空间列表 | 系统管理的工作空间模块 */
// TODO 工作空间管理员接口 /workspace 未区分
export function getSystemWorkspaceList() {
  return get<WorkspaceItem[]>(prefix)
}

/** 获取工作空间成员列表 **/
// TODO 工作空间管理员接口 /workspace 未区分

export function getWorkspaceMemberList(
  workspace_id: string,
  page: ParamsPage,
  query?: RequestParams,
) {
  return get<ResponsePage<WorkspaceItem>>(
    `${prefix}/${workspace_id}/user_list/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

export default {
  getSystemWorkspaceList,
}
