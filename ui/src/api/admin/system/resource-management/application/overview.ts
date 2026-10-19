/** System 资源管理智能体概览的使用统计与用户排行接口。 */
import { get } from '@/api/admin/core/request'
import type { ApplicationTokenUsage, ApplicationTopQuestion, HomeDateRange, HomeMonitoringDay } from '@/api/types'

const getPrefix = () => '/system/resource/application'

/** 获取智能体每日对话、用户、Tokens 与满意度统计。 */
const getMonitoring = (_workspaceId: string, range: HomeDateRange, applicationId: string) =>
  get<HomeMonitoringDay[]>(`${getPrefix()}/${applicationId}/application_stats`, { ...range })

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
