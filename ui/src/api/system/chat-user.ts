import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { ChatUserItem } from '@/api/type/systemChatUser'
import type { Ref } from 'vue'
const prefix = '/system/chat_user'


/**
 * 用户列表
 */
const getChatUserList: (loading?: Ref<boolean>) => Promise<Result<ChatUserItem[]>> = (loading) => {
  return get(`${prefix}/list`, undefined, loading)
}

/**
 * 用户分页列表
 * @query 参数
 username_or_nickname: string
 */
const getUserManage: (
  page: pageRequest,
  username_or_nickname: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, username_or_nickname, loading) => {
  return get(
    `${prefix}/user_manage/${page.current_page}/${page.page_size}`,
    username_or_nickname ? { username_or_nickname } : undefined,
    loading,
  )
}

/**
 * 删除用户
 * @param 参数 user_id,
 */
const delUserManage: (user_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  user_id,
  loading,
) => {
  return del(`${prefix}/${user_id}`, undefined, {}, loading)
}

/**
 * 创建用户
 */
const postUserManage: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 编辑用户
 */
const putUserManage: (
  user_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (user_id, data, loading) => {
  return put(`${prefix}/${user_id}`, data, undefined, loading)
}

/**
 * 修改用户密码
 */
const putUserManagePassword: (
  user_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (user_id, data, loading) => {
  return put(`${prefix}/${user_id}/re_password`, data, undefined, loading)
}


export default {
  getUserManage,
  putUserManage,
  delUserManage,
  postUserManage,
  putUserManagePassword,
  getChatUserList
}
