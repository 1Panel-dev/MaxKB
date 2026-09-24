import { postStream } from '@/api/admin/core/request'
import type { PromptGeneratePayload } from '@/api/types'
import { ADMIN_API_BASE_PATH } from '@/api/constants'

const prefix = '/system/shared/application'

/** 使用指定模型流式生成或优化 System 共享智能体的系统提示词。 */
const postPromptGenerate = (applicationId: string, modelId: string, payload: PromptGeneratePayload) => {
  return postStream(ADMIN_API_BASE_PATH, `${prefix}/${applicationId}/model/${modelId}/prompt_generate`, payload)
}

export default {
  postPromptGenerate,
}
