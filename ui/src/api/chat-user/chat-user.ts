import type { Ref } from 'vue'
import { Result } from '@/request/Result'
import { get, put } from '@/request/index'
import type { ChatUserGroupItem, ChatUserGroupUserItem, ChatUserResourceParams, putUserGroupUserParams } from '@/api/type/workspaceChatUser'
import type { pageRequest, PageList } from '@/api/type/common'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId()
  },
})
/**
 * 获取用户组列表
 */
const getUserGroupList: (resource: ChatUserResourceParams, loading?: Ref<boolean>) => Promise<Result<ChatUserGroupItem[]>> = (resource, loading) => {
  return get(`${prefix.value}/${resource.resource_type}/${resource.resource_id}/user_group`, undefined, loading)
}

/**
 * 修改用户组列表授权
 */
const editUserGroupList: (resource: ChatUserResourceParams, data: { user_group_id: string, is_auth: boolean }[], loading?: Ref<boolean>) => Promise<Result<any>> = (resource, data, loading) => {
  return put(`${prefix.value}/${resource.resource_type}/${resource.resource_id}/user_group`, data, undefined, loading)
}

/**
 * 获取用户组的用户列表
 */
const getUserGroupUserList: (
  resource: ChatUserResourceParams,
  user_group_id: string,
  page: pageRequest,
  username_or_nickname: string,
  loading?: Ref<boolean>,
) => Promise<Result<PageList<ChatUserGroupUserItem[]>>> = (resource, user_group_id, page, username_or_nickname, loading) => {
  return get(
    `${prefix.value}/${resource.resource_type}/${resource.resource_id}/user_group_id/${user_group_id}/${page.current_page}/${page.page_size}`,
    username_or_nickname ? { username_or_nickname } : undefined,
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
  return put(`${prefix.value}/${resource.resource_type}/${resource.resource_id}/user_group_id/${user_group_id}`, data, undefined, loading)
}

export default {
  getUserGroupList,
  editUserGroupList,
  getUserGroupUserList,
  putUserGroupUser
}
