import { del, get, getExportFile, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { ApplicationAccessToken, ApplicationAccessTokenPayload, ApplicationDetail, ApplicationFormPayload, Dict } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/application`
}

/**
 * 获取不分页的全部应用
 */
const getAllApplication = (query?: Dict<unknown>) => {
  return get<ApplicationDetail[]>(`${getPrefix()}`, query)
}

/** 获取工作空间智能体列表。 */
const getApplicationPage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ApplicationDetail>>(`${getPrefix()}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取工作空间智能体详情。 */
const getApplicationDetail = (applicationId: string) => {
  return get<ApplicationDetail>(`${getPrefix()}/${applicationId}`)
}

/** 获取智能体公开访问凭证与访问限制。 */
// TODO：社区版身份认证读写待后台联调。
const getAccessToken = (applicationId: string) => get<ApplicationAccessToken>(`${getPrefix()}/${applicationId}/access_token`)

/** 修改智能体访问配置或重置凭证，返回更新后的配置。 */
// TODO：身份认证、默认登录方式及账号锁定配置待后台联调。
const putAccessToken = (applicationId: string, payload: ApplicationAccessTokenPayload) =>
  put<ApplicationAccessTokenPayload, ApplicationAccessToken>(`${getPrefix()}/${applicationId}/access_token`, payload)

/** 保存智能体展示设置，沿用 V2 图片与配置的 multipart 协议。 */
const putDisplaySetting = (applicationId: string, payload: FormData) => put<FormData>(`${getPrefix()}/${applicationId}/setting`, payload)

/** 删除工作空间智能体。 */
const deleteApplication = (applicationId: string) => {
  return del<undefined, boolean>(`${getPrefix()}/${applicationId}`)
}

/** 导出工作空间智能体文件。 */
const exportApplication = (applicationId: string, applicationName: string) => {
  return getExportFile(`${applicationName}.mk`, `${getPrefix()}/${applicationId}/export`)
}

/** 模拟导出工作空间智能体为 Skills；TODO：接入真实下载接口。 */
const exportApplicationSkills = (applicationId: string, applicationName: string) =>
  Promise.resolve({ application_id: applicationId, name: applicationName })

/** 工作空间智能体上架到门户（仅已发布可上架）。 */
const putApplicationPortalUp = (applicationId: string) => put<Record<string, never>, ApplicationDetail>(`${getPrefix()}/${applicationId}/portal_up`)

/** 工作空间智能体从门户下架。 */
const putApplicationPortalDown = (applicationId: string) =>
  put<Record<string, never>, ApplicationDetail>(`${getPrefix()}/${applicationId}/portal_down`)

/** 导入智能体文件并创建工作空间智能体。 */
const postApplicationImport = (file: File, folderId: string) => {
  const payload = new FormData()
  payload.append('file', file)
  return post<FormData, ApplicationDetail>(`${getPrefix()}/folder/${folderId}/import`, payload)
}

/** 创建工作空间智能体。 */
const postApplication = (data: ApplicationFormPayload) => {
  return post<ApplicationFormPayload, ApplicationDetail>(getPrefix(), data)
}

/** 保存工作空间智能体配置。 */
const putApplication = (applicationId: string, data: ApplicationFormPayload) => {
  return put<ApplicationFormPayload, ApplicationDetail>(`${getPrefix()}/${applicationId}`, data)
}

/** 移动工作空间智能体。 */
const putMoveApplication = (applicationId: string, folderId: string) => {
  return put<Record<string, never>, boolean>(`${getPrefix()}/${applicationId}/move/${folderId}`, {})
}

/** 批量删除工作空间智能体。 */
const putBatchDeleteApplications = (applicationIds: string[]) => {
  return put<{ id_list: string[] }, boolean>(`${getPrefix()}/batch_delete`, { id_list: applicationIds })
}

/** 批量移动工作空间智能体。 */
const putBatchMoveApplications = (applicationIds: string[], folderId: string) => {
  return put<{ folder_id: string; id_list: string[] }, boolean>(`${getPrefix()}/batch_move`, { folder_id: folderId, id_list: applicationIds })
}

/** 发布工作空间智能体。 */
const putApplicationPublish = (applicationId: string, publishName: string, publishDesc?: string) => {
  return put<Record<string, unknown>, ApplicationDetail>(`${getPrefix()}/${applicationId}/publish`, {
    publish_name: publishName,
    publish_desc: publishDesc,
  })
}

export default {
  getApplicationPage,
  getApplicationDetail,
  getAccessToken,
  putAccessToken,
  putDisplaySetting,
  deleteApplication,
  exportApplication,
  exportApplicationSkills,
  putApplicationPortalUp,
  putApplicationPortalDown,
  postApplication,
  postApplicationImport,
  putApplication,
  putMoveApplication,
  putBatchDeleteApplications,
  putBatchMoveApplications,
  putApplicationPublish,
  getAllApplication,
}
