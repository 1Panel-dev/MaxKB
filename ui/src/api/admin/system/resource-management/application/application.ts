import { get, postStream } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { ApplicationDetail, Dict, PromptGeneratePayload } from '@/api/types'
import { ADMIN_API_BASE_PATH } from '@/api/constants'

const prefix = '/system/resource/application'

/** 获取 System 资源管理智能体分页列表。 */
const getApplicationPage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ApplicationDetail>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 使用指定模型流式生成或优化 System 资源智能体的系统提示词。 */
const postPromptGenerate = (applicationId: string, modelId: string, payload: PromptGeneratePayload) => {
  return postStream(ADMIN_API_BASE_PATH, `${prefix}/${applicationId}/model/${modelId}/prompt_generate`, payload)
}

export default {
  getApplicationPage,
  postPromptGenerate,
}
