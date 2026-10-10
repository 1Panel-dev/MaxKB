import { del, get, getExportFile } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { ApplicationDetail, Dict } from '@/api/types'

const prefix = '/system/resource/application'

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

export default {
  getApplicationPage,
  deleteApplication,
  exportApplication,
}
