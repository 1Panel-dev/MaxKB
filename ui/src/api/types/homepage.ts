/** 首页资源汇总，由后端按当前用户可见范围统计。 */
export interface HomeApplicationAggregation {
  total: number
  publish_count: number
  un_publish_count: number
}
export interface HomeKnowledgeAggregation {
  total: number
  document_count: number
  failure_count: number
}
export interface HomeToolAggregation {
  total: number
  custom_count: number
  workflow_count: number
  skill_count: number
  mcp_count: number
  data_source_count: number
}
export interface HomeModelAggregation {
  total: number
  llm_count: number
  embedding_count: number
}
export interface HomeDateRange {
  start_time: string
  end_time: string
}
export interface HomeMonitoringDay {
  day: string
  customer_num: number
  customer_added_count: number
  chat_record_count: number
  tokens_num: number
  star_num: number
  trample_num: number
}
/**
 * 首页排行类型：
 * - tokens：按智能体的 Tokens 消耗排行，数值取 total_tokens。
 * - questions：按智能体的对话次数排行，数值取 chat_record_count。
 * - userTokens：按用户的 Tokens 消耗排行，数值取 total_tokens，名称取 asker.username。
 */
export type HomeRankingKind = 'tokens' | 'questions' | 'userTokens'
export interface HomeRankingRecord {
  id?: string
  name?: string
  chat_user_id?: string
  chat_user_type?: string
  asker?: { username?: string } | null
  total_tokens?: number
  chat_record_count: number
  chat_user_count?: number
}
