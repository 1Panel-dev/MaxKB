import type { Ref } from 'vue'
import { Result } from '@/request/Result'
import { get, put } from '@/request/index'
import type { ChatUserGroupItem, ChatUserGroupUserItem, ChatUserResourceParams, putUserGroupUserParams } from '@/api/type/workspaceChatUser'
import type { pageRequest, PageList } from '@/api/type/common'
const prefix = '/workspace/' + localStorage.getItem('workspace_id')

/**
 * 获取用户组列表
 */
const getUserGroupList: (resource: ChatUserResourceParams, loading?: Ref<boolean>) => Promise<Result<ChatUserGroupItem[]>> = (resource, loading) => {
  return get(`${prefix}/${resource.resource_type}/${resource.resource_id}/user_group`, undefined, loading)
}

/**
 * 获取用户组的用户列表
 */
const getUserGroupUserList: (
  resource: ChatUserResourceParams,
  user_group_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<PageList<ChatUserGroupUserItem[]>>> = (resource, user_group_id, page, param, loading) => {
  return get(
    `${prefix}/${resource.resource_type}/${resource.resource_id}/user_group_id/${user_group_id}/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 更新用户组的用户列表
 */
const putUserGroupUser: (
  resource: ChatUserResourceParams,
  user_group_id: string,
  data: putUserGroupUserParams[],
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (resource, user_group_id, data, loading) => {
  return put(`${prefix}/${resource.resource_type}/${resource.resource_id}/user_group_id/${user_group_id}`, data, undefined, loading)
}

export default {
  getUserGroupList,
  getUserGroupUserList,
  putUserGroupUser
}