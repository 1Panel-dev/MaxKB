/** 工作空间智能体 API Key 接口。 */
import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { ApiKeyPayload, ApiKeyRecord, Dict } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (applicationId: string) => `/workspace/${getWorkspaceId()}/application/${applicationId}/application_key`

/** 分页查询智能体 API Key。 */
const getApiKeyPage = (applicationId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<ApiKeyRecord>>(`${getPrefix(applicationId)}/${page.currentPage}/${page.pageSize}`, query)

/** 生成智能体 API Key。 */
const postApiKey = (applicationId: string) => post<Record<string, never>, ApiKeyRecord>(getPrefix(applicationId), {})

/** 修改智能体 API Key 配置或启用状态。 */
const putApiKey = (applicationId: string, apiKeyId: string, payload: ApiKeyPayload) =>
  put<ApiKeyPayload, boolean>(`${getPrefix(applicationId)}/${apiKeyId}`, payload)

/** 删除智能体 API Key。 */
const deleteApiKey = (applicationId: string, apiKeyId: string) => del<undefined, void>(`${getPrefix(applicationId)}/${apiKeyId}`)

export default {
  getApiKeyPage,
  postApiKey,
  putApiKey,
  deleteApiKey,
}
