import { del, get, post, put } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { ApiKeyPayload, ApiKeyRecord, Dict } from '@/api/types'

const prefix = '/system/api_key'

/** 分页查询系统 API Key。 */
const getApiKeyPage = (page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<ApiKeyRecord>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)

/** 生成系统 API Key。 */
const postApiKey = () => post<Record<string, never>, ApiKeyRecord>(prefix, {})

/** 修改系统 API Key 配置或启用状态。 */
const putApiKey = (apiKeyId: string, payload: ApiKeyPayload) => put<ApiKeyPayload, boolean>(`${prefix}/${apiKeyId}`, payload)

/** 删除系统 API Key。 */
const deleteApiKey = (apiKeyId: string) => del<undefined, boolean>(`${prefix}/${apiKeyId}`)

export default {
  getApiKeyPage,
  postApiKey,
  putApiKey,
  deleteApiKey,
}
