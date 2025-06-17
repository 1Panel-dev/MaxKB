import { get, post, del } from '@/request/index'
import type { Ref } from 'vue'
import { Result } from '@/request/Result'
import type { RoleItem, RolePermissionItem, CreateOrUpdateParams, RoleMemberItem, CreateMemberParamsItem } from '@/api/type/role'
import { RoleTypeEnum } from '@/enums/system'
import type { pageRequest, PageList } from '@/api/type/common'

const prefix = '/workspace/role'
/**
 * 获取角色列表
 */
const getRoleList: (loading?: Ref<boolean>) => Promise<Result<{ internal_role: RoleItem[], custom_role: RoleItem[] }>> = (loading) => {
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

export default {
  getRoleList,
  CreateMember,
}
