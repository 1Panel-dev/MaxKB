import { get, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  ApplicationDetail,
  ApplicationFormPayload,
  RequestParams,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/application`
}

/** 获取工作空间智能体列表。 */
const getApplicationPage = (page: ParamsPage, query?: RequestParams) => {
  return get<ResponsePage<ApplicationDetail>>(
    `${getPrefix()}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 获取工作空间智能体详情。 */
const getApplicationDetail = (applicationId: string) => {
  return get<ApplicationDetail>(`${getPrefix()}/${applicationId}`)
}

/** 保存工作空间智能体配置。 */
const putApplication = (applicationId: string, data: ApplicationFormPayload) => {
  return put<ApplicationFormPayload, ApplicationDetail>(`${getPrefix()}/${applicationId}`, data)
}

export default {
  getApplicationPage,
  getApplicationDetail,
  putApplication,
}
