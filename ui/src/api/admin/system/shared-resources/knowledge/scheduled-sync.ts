import { get, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { KnowledgeSyncLog, KnowledgeSyncSetting } from '@/api/types'

const getPrefix = (knowledgeId: string) => `/system/shared/knowledge/${knowledgeId}`

/** 获取知识库定时同步设置。 */
const getKnowledgeSyncSetting = (knowledgeId: string) => get<KnowledgeSyncSetting>(`${getPrefix(knowledgeId)}/sync_setting`)

/** 保存知识库定时同步设置。 */
const putKnowledgeSyncSetting = (knowledgeId: string, setting: KnowledgeSyncSetting) =>
  put<KnowledgeSyncSetting, KnowledgeSyncSetting>(`${getPrefix(knowledgeId)}/sync_setting`, setting)

/** 获取知识库同步日志分页。 */
const getKnowledgeSyncLogPage = (knowledgeId: string, page: ParamsPage) =>
  get<ResponsePage<KnowledgeSyncLog>>(`${getPrefix(knowledgeId)}/sync_log/${page.currentPage}/${page.pageSize}`)

export default { getKnowledgeSyncSetting, putKnowledgeSyncSetting, getKnowledgeSyncLogPage }
