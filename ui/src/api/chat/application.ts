/** 提供对话端智能体信息接口。 */

import type { ChatApplicationProfile } from '@/api/types'
import { get } from './core/request'

/** 获取智能体的名称、图标、开场白等对话所需信息。 */
const getApplicationProfile = (applicationId: string) => {
  return get<ChatApplicationProfile>(`/v3/application/${applicationId}/profile`)
}

export default { getApplicationProfile }
