/** System 资源管理智能体概览的使用统计与用户排行接口。 */
import { get, getExportFile } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { ApplicationRankingKind, HomeDateRange, HomeMonitoringDay, HomeRankingRecord } from '@/api/types'

const getPrefix = () => '/system/resource/application'

/** 获取智能体每日对话、用户、Tokens 与满意度统计。 */
const getMonitoring = (_workspaceId: string, range: HomeDateRange, applicationId: string) =>
  get<HomeMonitoringDay[]>(`${getPrefix()}/${applicationId}/application_stats`, { ...range })

// TODO：后台按首页协议补齐用户排行分页、name 搜索、汇总和导出。
const rankingPaths = { userTokens: 'application_token_usage', questions: 'top_questions' }

/** 分页查询当前智能体的用户排行。 */
const getRanking = (applicationId: string, kind: ApplicationRankingKind, page: ParamsPage, range: HomeDateRange, name?: string) =>
  get<ResponsePage<HomeRankingRecord>>(`${getPrefix()}/${applicationId}/${rankingPaths[kind]}/${page.currentPage}/${page.pageSize}`, {
    ...range,
    ...(name ? { name } : {}),
  })

/** 获取当前智能体同期 Tokens 总量。 */
const getTokensAggregation = (applicationId: string, range: HomeDateRange) =>
  get<number>(`${getPrefix()}/${applicationId}/tokens/aggregation`, { ...range })

/** 获取当前智能体同期对话次数。 */
const getChatRecordAggregation = (applicationId: string, range: HomeDateRange) =>
  get<number>(`${getPrefix()}/${applicationId}/chat_record/aggregation`, { ...range })

/** 按日期与用户名筛选导出完整用户排行。 */
const exportRanking = (applicationId: string, kind: ApplicationRankingKind, range: HomeDateRange, name?: string) =>
  getExportFile(`${rankingPaths[kind]}.xlsx`, `${getPrefix()}/${applicationId}/${rankingPaths[kind]}/export`, {
    ...range,
    ...(name ? { name } : {}),
  })

export default {
  getMonitoring,
  getRanking,
  getTokensAggregation,
  getChatRecordAggregation,
  exportRanking,
}
