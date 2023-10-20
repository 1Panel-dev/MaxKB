import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
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
const postCreatTeamMember: (request: TeamMemberRequest) => Promise<Result<boolean>> = (request) => {
  return post(`${prefix}`, request)
}

export default {
  getTeamMember,
  postCreatTeamMember
}
