import { Result } from '@/request/Result'
import { get, post, del } from '@/request/index'
import type { TeamMember, TeamMemberRequest } from '@/api/type/team'
// import type { Ref } from 'vue'

const prefix = '/team/member'

/**
 * 获取团队成员列表
 */
const getTeamMember: () => Promise<Result<TeamMember[]>> = () => {
  return get(`${prefix}`)
}

/**
 * 添加成员
 * @param 参数 { "username_or_email": "string" }
 */
const postCreatTeamMember: (body: TeamMemberRequest) => Promise<Result<boolean>> = (body) => {
  return post(`${prefix}`, body)
}

/**
 * 删除成员
 * @param 参数 member_id
 */
const delTeamMember: (member_id: String) => Promise<Result<boolean>> = (member_id) => {
  return del(`${prefix}/${member_id}`)
}

/**
 * 获取成员权限
 * @param 参数 member_id
 */
const getMemberPermissions: (member_id: String) => Promise<Result<any>> = (member_id) => {
  return get(`${prefix}/${member_id}`)
}

export default {
  getTeamMember,
  postCreatTeamMember,
  delTeamMember,
  getMemberPermissions
}
