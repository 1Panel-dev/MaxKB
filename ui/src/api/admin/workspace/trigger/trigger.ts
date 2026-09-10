import { get, post, put, del } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, Trigger, TriggerDetail, TriggerPayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => `/workspace/${getWorkspaceId()}/trigger`

/** 获取当前工作空间的触发器分页列表。 */
const getTriggerPage = (page: ParamsPage, query: Dict<unknown> = {}) =>
  get<ResponsePage<Trigger>>(`${getPrefix()}/${page.currentPage}/${page.pageSize}`, query)
/** 获取触发器配置和关联任务详情。 */
const getTriggerDetail = (triggerId: string) => get<TriggerDetail>(`${getPrefix()}/${triggerId}`)
/** 创建触发器及关联任务。 */
const postTrigger = (payload: TriggerPayload) => post<TriggerPayload, TriggerPayload>(getPrefix(), payload)
/** 更新触发器配置或启用状态。 */
const putTrigger = (triggerId: string, payload: Partial<TriggerPayload>) =>
  put<Partial<TriggerPayload>, TriggerDetail>(`${getPrefix()}/${triggerId}`, payload)
/** 删除触发器及关联记录。 */
const deleteTrigger = (triggerId: string) => del<undefined, boolean>(`${getPrefix()}/${triggerId}`)
/** 批量删除触发器。 */
const putBatchDeleteTrigger = (triggerIds: string[]) => put<{ id_list: string[] }, boolean>(`${getPrefix()}/batch_delete`, { id_list: triggerIds })
/** 批量启用或禁用触发器。 */
const putBatchActivateTrigger = (triggerIds: string[], isActive: boolean) =>
  put<{ id_list: string[]; is_active: boolean }, boolean>(`${getPrefix()}/batch_activate`, { id_list: triggerIds, is_active: isActive })

export default { getTriggerPage, getTriggerDetail, postTrigger, putTrigger, deleteTrigger, putBatchDeleteTrigger, putBatchActivateTrigger }
