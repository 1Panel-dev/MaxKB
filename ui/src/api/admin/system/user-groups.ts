import type { ListItem } from '@/api/types'

export interface SystemUserGroupRequest {
  id?: string
  name: string
  workspaceId: string
}

/**
 * 创建或重命名系统用户组。
 * TODO 后端接口就绪后，在此接入 Admin 请求层并移除本地占位返回。
 */
function postSystemUserGroup(group: SystemUserGroupRequest) {
  return Promise.resolve<ListItem>({
    id: group.id ?? crypto.randomUUID(),
    name: group.name,
  })
}

/**
 * 删除系统用户组。
 * TODO 后端接口就绪后，在此接入 Admin 请求层并移除本地占位返回。
 */
function deleteSystemUserGroup(_workspaceId: string, _groupId: string) {
  return Promise.resolve(true)
}

/**
 * 移除系统用户组成员。
 * TODO 后端接口就绪后，在此接入 Admin 请求层并移除本地占位返回。
 */
function postRemoveSystemUserGroupMembers(
  _workspaceId: string,
  _groupId: string,
  _memberIds: Array<number | string>,
) {
  return Promise.resolve(true)
}

export default {
  deleteSystemUserGroup,
  postSystemUserGroup,
  postRemoveSystemUserGroupMembers,
}
