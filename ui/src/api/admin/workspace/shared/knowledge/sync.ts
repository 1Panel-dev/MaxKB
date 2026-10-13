import { get } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type { KnowledgeSyncLog, KnowledgeSyncSetting } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}`

/** 获取知识库定时同步设置。 */
const getKnowledgeSyncSetting = (knowledgeId: string) => get<KnowledgeSyncSetting>(`${getPrefix(knowledgeId)}/sync_setting`)

/** 获取知识库同步日志分页。 */
const getKnowledgeSyncLogPage = (knowledgeId: string, page: ParamsPage) =>
  get<ResponsePage<KnowledgeSyncLog>>(`${getPrefix(knowledgeId)}/sync_log/${page.currentPage}/${page.pageSize}`)

export default { getKnowledgeSyncSetting, getKnowledgeSyncLogPage }
