import { del, get, getExportFile, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { ApplicationDetail, ApplicationFormPayload, Dict } from '@/api/types'

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

/** 获取 System 资源管理智能体详情。 */
const getApplicationDetail = (applicationId: string) => get<ApplicationDetail>(`${prefix}/${applicationId}`)

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
  putApplication,
  putApplicationPublish,
  getAllApplication,
  getApplicationPage,
  deleteApplication,
  exportApplication,
}
