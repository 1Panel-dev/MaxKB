import { get, getExportFile } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type {
  Dict,
  HomeApplicationAggregation,
  HomeKnowledgeAggregation,
  HomeToolAggregation,
  HomeModelAggregation,
  HomeDateRange,
  HomeMonitoringDay,
  HomeRankingKind,
  HomeRankingRecord,
} from '@/api/types'

const prefix = `/system/homepage`

/** 合并系统首页的工作空间筛选条件。 */
const withWorkspaceId = (workspaceId: string, query: Dict<unknown> = {}) => ({
  ...query,
  workspace_id: workspaceId,
})
/** 获取智能体数量与发布状态。 */
const getApplicationAggregation = (workspaceId: string) =>
  get<HomeApplicationAggregation>(`${prefix}/application/aggregation`, withWorkspaceId(workspaceId))
/** 获取知识库与文档数量。 */
const getKnowledgeAggregation = (workspaceId: string) =>
  get<HomeKnowledgeAggregation>(`${prefix}/knowledge/aggregation`, withWorkspaceId(workspaceId))
/** 获取工具数量与类型分布。 */
const getToolAggregation = (workspaceId: string) => get<HomeToolAggregation>(`${prefix}/tool/aggregation`, withWorkspaceId(workspaceId))
/** 获取模型数量与类型分布。 */
const getModelAggregation = (workspaceId: string) => get<HomeModelAggregation>(`${prefix}/model/aggregation`, withWorkspaceId(workspaceId))
/** 获取指定日期及智能体范围内的每日使用趋势。 */
const getMonitoring = (workspaceId: string, range: HomeDateRange, applicationId?: string) =>
  get<HomeMonitoringDay[]>(
    `${prefix}/monitoring/aggregation`,
    withWorkspaceId(workspaceId, {
      ...range,
      ...(applicationId ? { application_id: applicationId } : {}),
    }),
  )
/** 获取工作空间日期范围内的 Tokens 总量。 */
const getTokensAggregation = (workspaceId: string, range: HomeDateRange) =>
  get<number>(`${prefix}/tokens/aggregation`, withWorkspaceId(workspaceId, { ...range }))
/** 获取工作空间日期范围内的对话轮次。 */
const getChatRecordAggregation = (workspaceId: string, range: HomeDateRange) =>
  get<number>(`${prefix}/chat_record/aggregation`, withWorkspaceId(workspaceId, { ...range }))

const rankingPaths = { tokens: 'tokens_ranking', questions: 'question_ranking', userTokens: 'user_tokens_ranking' }

/** 分页查询智能体或用户使用排行。 */
const getRanking = (workspaceId: string, kind: HomeRankingKind, page: ParamsPage, range: HomeDateRange, name?: string) =>
  get<ResponsePage<HomeRankingRecord>>(
    `${prefix}/application/${rankingPaths[kind]}/${page.currentPage}/${page.pageSize}`,
    withWorkspaceId(workspaceId, { ...range, ...(name ? { name } : {}) }),
  )
/** 按当前日期与名称筛选导出完整排行。 */
const exportRanking = (workspaceId: string, kind: HomeRankingKind, range: HomeDateRange, name?: string) =>
  getExportFile(
    `${rankingPaths[kind]}.xlsx`,
    `${prefix}/${rankingPaths[kind]}/export`,
    withWorkspaceId(workspaceId, { ...range, ...(name ? { name } : {}) }),
  )

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
