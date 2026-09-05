import { get } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, Trigger } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

/** 获取当前工作空间的触发器分页列表。 */
const getTriggerPage = (page: ParamsPage, query: Dict<unknown> = {}) => {
  return get<ResponsePage<Trigger>>(`/workspace/${getWorkspaceId()}/trigger/${page.currentPage}/${page.pageSize}`, query)
}

export default { getTriggerPage }
