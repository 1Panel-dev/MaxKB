import {Result} from '@/request/Result'
import {get, post, del} from '@/request/index'
import type {Ref} from 'vue'
import type {ChatUserGroupUserItem,} from '@/api/type/systemChatUser'
import type {pageRequest, PageList, ListItem} from '@/api/type/common'

const prefix = '/workspace/group'

/**
 * 获取用户组列表
 */
const getUserGroup: (loading?: Ref<boolean>) => Promise<Result<ListItem[]>> = () => {
  return get(`${prefix}`)
}

/**
 * 创建用户组
 * @param 参数
 * {
 "id": "string",
 "name": "string"
 }
 */
const postUserGroup: (data: ListItem, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  data,
  loading,
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 删除用户组
 * @param 参数 user_group_id
 */
const delUserGroup: (user_group_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  user_group_id,
  loading,
) => {
  return del(`${prefix}/${user_group_id}`, undefined, {}, loading)
}

/**
 * 给用户组添加用户
 */
const postAddMember: (
  user_group_id: string,
  body: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (user_group_id, body, loading) => {
  return post(`${prefix}/${user_group_id}/add_member`, body, {}, loading)
}

/**
 * 从用户组删除用户
 */
const postRemoveMember: (
  user_group_id: string,
  body: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (user_group_id, body, loading) => {
  return post(`${prefix}/${user_group_id}/remove_member`, body, {}, loading)
}

/**
 * 获取用户组的成员列表
 */
const getUserListByGroup: (
  user_group_id: string,
  page: pageRequest,
  params ?: any,
  loading?: Ref<boolean>,
) => Promise<Result<PageList<ChatUserGroupUserItem[]>>> = (user_group_id, page, params, loading) => {
  return get(
    `${prefix}/${user_group_id}/user_list/${page.current_page}/${page.page_size}`,
    params ? params : undefined,
    loading,
  )
}
export default {
  getUserGroup,
  postUserGroup,
  delUserGroup,
  postAddMember,
  postRemoveMember,
  getUserListByGroup
}
