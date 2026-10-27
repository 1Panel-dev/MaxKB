import { del, get, getExportFile, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type {
  ApplicationAccessToken,
  ApplicationAccessTokenPayload,
  ApplicationDetail,
  ApplicationDisplaySetting,
  ApplicationFormPayload,
  Dict,
} from '@/api/types'

const prefix = '/system/resource/application'

/** 获取 System 资源管理不分页的智能体列表。 */
const getAllApplication = (query?: Dict<unknown>) => get<ApplicationDetail[]>(prefix, query)

/** 获取 System 资源管理智能体分页列表。 */
const getApplicationPage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ApplicationDetail>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 删除系统资源管理智能体。 */
const deleteApplication = (applicationId: string) => {
  return del<undefined, boolean>(`${prefix}/${applicationId}`)
}

/** 导出系统资源管理智能体文件。 */
const exportApplication = (applicationId: string, applicationName: string) => {
  return getExportFile(`${applicationName}.mk`, `${prefix}/${applicationId}/export`)
}

/** 模拟 System 资源管理智能体 Skills 导出；TODO：接入真实下载接口。 */
const exportApplicationSkills = (applicationId: string, applicationName: string) =>
  Promise.resolve({ application_id: applicationId, name: applicationName })

/** System 资源管理智能体上架到门户（仅已发布可上架）。 */
const putApplicationPortalUp = (applicationId: string) => put<Record<string, never>, ApplicationDetail>(`${prefix}/${applicationId}/portal_up`)

/** System 资源管理智能体从门户下架。 */
const putApplicationPortalDown = (applicationId: string) => put<Record<string, never>, ApplicationDetail>(`${prefix}/${applicationId}/portal_down`)

/** 获取 System 资源管理智能体详情。 */
const getApplicationDetail = (applicationId: string) => get<ApplicationDetail>(`${prefix}/${applicationId}`)

/** 获取 System 资源管理智能体公开访问凭证与访问限制。 */
const getAccessToken = (applicationId: string) => get<ApplicationAccessToken>(`${prefix}/${applicationId}/access_token`)

/** 修改 System 资源管理智能体访问配置或重置凭证，返回更新后的配置。 */
// 身份认证、默认登录方式及账号锁定配置待后台联调。
const putAccessToken = (applicationId: string, payload: ApplicationAccessTokenPayload) =>
  put<ApplicationAccessTokenPayload, ApplicationAccessToken>(`${prefix}/${applicationId}/access_token`, payload)

/** 获取智能体展示设置，仅许可证有效的专业版、企业版提供；未保存过的字段可能缺失。 */
const getDisplaySetting = (applicationId: string) => get<Partial<ApplicationDisplaySetting>>(`${prefix}/${applicationId}/setting`)

/** 保存智能体展示设置，沿用 V2 图片与配置的 multipart 协议。 */
const putDisplaySetting = (applicationId: string, payload: FormData) => put<FormData>(`${prefix}/${applicationId}/setting`, payload)

/** 保存 System 资源管理智能体配置。 */
const putApplication = (applicationId: string, data: ApplicationFormPayload) =>
  put<ApplicationFormPayload, ApplicationDetail>(`${prefix}/${applicationId}`, data)

/** 发布 System 资源管理智能体。 */
const putApplicationPublish = (applicationId: string, publishName: string, publishDesc?: string) =>
  put<Record<string, unknown>, ApplicationDetail>(`${prefix}/${applicationId}/publish`, {
    publish_name: publishName,
    publish_desc: publishDesc,
  })

export default {
  getApplicationDetail,
  getAccessToken,
  putAccessToken,
  getDisplaySetting,
  putDisplaySetting,
  putApplication,
  putApplicationPublish,
  getAllApplication,
  getApplicationPage,
  deleteApplication,
  exportApplication,
  exportApplicationSkills,
  putApplicationPortalUp,
  putApplicationPortalDown,
}
