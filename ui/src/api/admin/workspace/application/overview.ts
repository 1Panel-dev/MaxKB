/** 工作空间智能体概览的使用统计与用户排行接口。 */
import { get } from '../../core/request'
import type { ApplicationTokenUsage, ApplicationTopQuestion, HomeDateRange, HomeMonitoringDay } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (workspaceId = getWorkspaceId()) => `/workspace/${workspaceId}/application`

/** 获取智能体每日对话、用户、Tokens 与满意度统计。 */
const getMonitoring = (workspaceId: string, range: HomeDateRange, applicationId: string) =>
  get<HomeMonitoringDay[]>(`${getPrefix(workspaceId)}/${applicationId}/application_stats`, { ...range })

/** 获取智能体按用户排序的 Tokens 消耗。 */
const getTokenUsage = (applicationId: string, range: HomeDateRange) =>
  get<ApplicationTokenUsage[]>(`${getPrefix()}/${applicationId}/application_token_usage`, { ...range })

/** 获取智能体按用户排序的提问次数。 */
const getTopQuestions = (applicationId: string, range: HomeDateRange) =>
  get<ApplicationTopQuestion[]>(`${getPrefix()}/${applicationId}/top_questions`, { ...range })

export default {
  getMonitoring,
  getTokenUsage,
  getTopQuestions,
}
