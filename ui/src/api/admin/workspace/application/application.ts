import { get, post, put } from '../../core/request'
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

/** 发布工作空间智能体。 */
const putApplicationPublish = (applicationId: string) => {
  return put<Record<string, never>, ApplicationDetail>(`${getPrefix()}/${applicationId}/publish`, {})
}

export default { getApplicationPage, getApplicationDetail, postApplicationImport, putApplication, putApplicationPublish }
