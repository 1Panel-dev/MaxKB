import { get, getExportFile } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type {
  HomeApplicationAggregation,
  HomeKnowledgeAggregation,
  HomeToolAggregation,
  HomeModelAggregation,
  HomeDateRange,
  HomeMonitoringDay,
  HomeRankingKind,
  HomeRankingRecord,
} from '@/api/types'

const getPrefix = (workspaceId: string) => `/workspace/${workspaceId}/homepage`
/** 获取智能体数量与发布状态。 */
const getApplicationAggregation = (workspaceId: string) => get<HomeApplicationAggregation>(`${getPrefix(workspaceId)}/application/aggregation`)
/** 获取知识库与文档数量。 */
const getKnowledgeAggregation = (workspaceId: string) => get<HomeKnowledgeAggregation>(`${getPrefix(workspaceId)}/knowledge/aggregation`)
/** 获取工具数量与类型分布。 */
const getToolAggregation = (workspaceId: string) => get<HomeToolAggregation>(`${getPrefix(workspaceId)}/tool/aggregation`)
/** 获取模型数量与类型分布。 */
const getModelAggregation = (workspaceId: string) => get<HomeModelAggregation>(`${getPrefix(workspaceId)}/model/aggregation`)
/** 获取指定日期及智能体范围内的每日使用趋势。 */
const getMonitoring = (workspaceId: string, range: HomeDateRange, applicationId?: string) =>
  get<HomeMonitoringDay[]>(`${getPrefix(workspaceId)}/monitoring/aggregation`, {
    ...range,
    ...(applicationId ? { application_id: applicationId } : {}),
  })
/** 获取工作空间日期范围内的 Tokens 总量。 */
const getTokensAggregation = (workspaceId: string, range: HomeDateRange) => get<number>(`${getPrefix(workspaceId)}/tokens/aggregation`, { ...range })
/** 获取工作空间日期范围内的对话轮次。 */
const getChatRecordAggregation = (workspaceId: string, range: HomeDateRange) =>
  get<number>(`${getPrefix(workspaceId)}/chat_record/aggregation`, { ...range })

const rankingPaths = { tokens: 'tokens_ranking', questions: 'question_ranking', userTokens: 'user_tokens_ranking' }

/** 分页查询智能体或用户使用排行。 */
const getRanking = (workspaceId: string, kind: HomeRankingKind, page: ParamsPage, range: HomeDateRange, name?: string) =>
  get<ResponsePage<HomeRankingRecord>>(`${getPrefix(workspaceId)}/application/${rankingPaths[kind]}/${page.currentPage}/${page.pageSize}`, {
    ...range,
    ...(name ? { name } : {}),
  })
/** 按当前日期与名称筛选导出完整排行。 */
const exportRanking = (workspaceId: string, kind: HomeRankingKind, range: HomeDateRange, name?: string) =>
  getExportFile(`${rankingPaths[kind]}.xlsx`, `${getPrefix(workspaceId)}/${rankingPaths[kind]}/export`, { ...range, ...(name ? { name } : {}) })

export default {
  getApplicationAggregation,
  getKnowledgeAggregation,
  getToolAggregation,
  getModelAggregation,
  getMonitoring,
  getTokensAggregation,
  getChatRecordAggregation,
  getRanking,
  exportRanking,
}
