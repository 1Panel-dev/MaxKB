import { del, get, getExportFile, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { ApplicationDetail, ApplicationFormPayload, Dict } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/application`
}

/** 获取工作空间智能体列表。 */
const getApplicationPage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ApplicationDetail>>(`${getPrefix()}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取工作空间智能体详情。 */
const getApplicationDetail = (applicationId: string) => {
  return get<ApplicationDetail>(`${getPrefix()}/${applicationId}`)
}

/** 删除工作空间智能体。 */
const deleteApplication = (applicationId: string) => {
  return del<undefined, boolean>(`${getPrefix()}/${applicationId}`)
}

/** 导出工作空间智能体文件。 */
const exportApplication = (applicationId: string, applicationName: string) => {
  return getExportFile(`${applicationName}.mk`, `${getPrefix()}/${applicationId}/export`)
}

/** 导入智能体文件并创建工作空间智能体。 */
const postApplicationImport = (file: File, folderId: string) => {
  const payload = new FormData()
  payload.append('file', file)
  return post<FormData, ApplicationDetail>(`${getPrefix()}/folder/${folderId}/import`, payload)
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
const putApplicationPublish = (applicationId: string) => {
  return put<Record<string, never>, ApplicationDetail>(`${getPrefix()}/${applicationId}/publish`, {})
}

export default {
  getApplicationPage,
  getApplicationDetail,
  deleteApplication,
  exportApplication,
  postApplicationImport,
  putApplication,
  putMoveApplication,
  putBatchDeleteApplications,
  putBatchMoveApplications,
  putApplicationPublish,
}
