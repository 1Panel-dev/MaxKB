/** System 资源管理智能体发布渠道配置与启停接口。 */
import { get, post } from '@/api/admin/core/request'
import type { ApplicationAccessConfig, ApplicationAccessPlatform, ApplicationAccessStatus, ApplicationAccessStatusPayload } from '@/api/types'

const getPrefix = (applicationId: string) => `/system/resource/application/${applicationId}/platform`

/** 获取智能体各发布渠道的配置及启用状态。 */
const getPlatformStatus = (applicationId: string) => get<ApplicationAccessStatus>(`${getPrefix(applicationId)}/status`)

/** 启用或停用智能体发布渠道。 */
const postPlatformStatus = (applicationId: string, payload: ApplicationAccessStatusPayload) => post(`${getPrefix(applicationId)}/status`, payload)

/** 获取智能体指定发布渠道的配置。 */
const getPlatformConfig = (applicationId: string, platform: ApplicationAccessPlatform) =>
  get<ApplicationAccessConfig | null>(`${getPrefix(applicationId)}/${platform}`)

/** 保存智能体指定发布渠道的配置。 */
const postPlatformConfig = (applicationId: string, platform: ApplicationAccessPlatform, payload: ApplicationAccessConfig) =>
  post(`${getPrefix(applicationId)}/${platform}`, payload)

export default { getPlatformStatus, postPlatformStatus, getPlatformConfig, postPlatformConfig }
