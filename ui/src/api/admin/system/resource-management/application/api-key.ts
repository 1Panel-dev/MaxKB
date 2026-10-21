/** System 资源管理智能体 API Key 接口。TODO：接口待联调。 */
import { del, get, post, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { ApiKeyPayload, ApiKeyRecord, Dict } from '@/api/types'

const getPrefix = (applicationId: string) => `/system/resource/application/${applicationId}/application_key`

/** 分页查询智能体 API Key。 */
const getApiKeyPage = (applicationId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<ApiKeyRecord>>(`${getPrefix(applicationId)}/${page.currentPage}/${page.pageSize}`, query)

/** 生成智能体 API Key。 */
const postApiKey = (applicationId: string) => post<Record<string, never>, ApiKeyRecord>(getPrefix(applicationId), {})

/** 修改智能体 API Key 配置或启用状态。 */
const putApiKey = (applicationId: string, apiKeyId: string, payload: ApiKeyPayload) =>
  put<ApiKeyPayload, boolean>(`${getPrefix(applicationId)}/${apiKeyId}`, payload)

/** 删除智能体 API Key。 */
const deleteApiKey = (applicationId: string, apiKeyId: string) => del<undefined, boolean>(`${getPrefix(applicationId)}/${apiKeyId}`)

export default {
  getApiKeyPage,
  postApiKey,
  putApiKey,
  deleteApiKey,
}
