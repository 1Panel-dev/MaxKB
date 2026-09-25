import { get } from '../../core/request'
import type { Dict, ModelItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => `/system/shared/workspace/${getWorkspaceId()}/model`

/** 获取工作空间共享的模型列表。 */
const getModelList = (query?: Dict<unknown>) => {
  return get<ModelItem[]>(getPrefix(), query)
}

export default { getModelList }
