import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { TeamMember } from '@/api/type/team'

const prefix = '/team/member'

/**
 * 獲取團隊成員列表
 */
const getTeamMember: () => Promise<Result<TeamMember[]>> = () => {
  return get(`${prefix}`)
}

/**
 * 添加成員
 * @param 參數 []
 */
const postCreatTeamMember: (data: Array<String>) => Promise<Result<boolean>> = (data) => {
  return post(`${prefix}/_batch`, data)
}

/**
 * 刪除成員
 * @param 參數 member_id
 */
const delTeamMember: (member_id: String) => Promise<Result<boolean>> = (member_id) => {
  return del(`${prefix}/${member_id}`)
}

/**
 * 獲取成員權限
 * @param 參數 member_id
 */
const getMemberPermissions: (member_id: String) => Promise<Result<any>> = (member_id) => {
  return get(`${prefix}/${member_id}`)
}

/**
 * 獲取成員權限
 * @param 參數 member_id
 * @param 參數 {
          "team_member_permission_list": [
            {
              "target_id": "string",
              "type": "string",
              "operate": {
                "USE": true,
                "MANAGE": true
              }
            }
          ]
        }
 */
const putMemberPermissions: (member_id: String, body: any) => Promise<Result<any>> = (
  member_id,
  body
) => {
  return put(`${prefix}/${member_id}`, body)
}

export default {
  getTeamMember,
  postCreatTeamMember,
  delTeamMember,
  getMemberPermissions,
  putMemberPermissions
}
