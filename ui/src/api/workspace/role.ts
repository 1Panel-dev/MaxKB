import { get, post, del } from '@/request/index'
import type { Ref } from 'vue'
import { Result } from '@/request/Result'
import type {
  RoleItem,
  RoleMemberItem,
  CreateMemberParamsItem,
} from '@/api/type/role'
import type { pageRequest, PageList } from '@/api/type/common'

const prefix = '/workspace/role'
/**
 * 获取角色列表
 */
const getRoleList: (
  loading?: Ref<boolean>,
) => Promise<Result<{ internal_role: RoleItem[]; custom_role: RoleItem[] }>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 新建角色成员
 */
const CreateMember: (
  role_id: string,
  data: { members: CreateMemberParamsItem[] },
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (role_id, data, loading) => {
  return post(`${prefix}/${role_id}/add_member`, data, undefined, loading)
}

/**
 * 获取角色成员列表
 */
const getRoleMemberList: (
  role_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<PageList<RoleMemberItem[]>>> = (role_id, page, param, loading) => {
  return get(
    `${prefix}/${role_id}/user_list/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 删除角色成员
 */
const deleteRoleMember: (
  role_id: string,
  user_relation_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (role_id, user_relation_id, loading) => {
  return del(`${prefix}/${role_id}/remove_member/${user_relation_id}`, undefined, {}, loading)
}

export default {
  getRoleList,
  CreateMember,
  getRoleMemberList,
  deleteRoleMember,
}
