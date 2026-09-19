import { get, post, put, del } from '../../core/request'
import type { ResourceTrigger, ResourceTriggerDetail, ResourceTriggerResource, TriggerPayload } from '@/api/types'

const getPrefix = (resource: ResourceTriggerResource) => `/workspace/${resource.workspace_id}/${resource.source_type}/${resource.source_id}/trigger`

/** 查询当前资源关联的已启用触发器。 */
const getResourceTriggerList = (resource: ResourceTriggerResource) => get<ResourceTrigger[]>(getPrefix(resource))

/** 查询触发器配置及当前资源的执行任务。 */
const getResourceTriggerDetail = (resource: ResourceTriggerResource, triggerId: string) =>
  get<ResourceTriggerDetail>(`${getPrefix(resource)}/${triggerId}`)

/** 为当前资源创建只有一个执行任务的触发器。 */
const postResourceTrigger = (resource: ResourceTriggerResource, payload: TriggerPayload) =>
  post<TriggerPayload, ResourceTrigger>(getPrefix(resource), payload)

/** 更新触发器配置及当前资源的任务参数，保留其他资源任务。 */
const putResourceTrigger = (resource: ResourceTriggerResource, triggerId: string, payload: TriggerPayload) =>
  put<TriggerPayload, ResourceTriggerDetail>(`${getPrefix(resource)}/${triggerId}`, payload)

/** 移除当前资源与触发器的关联，最后一个任务移除时删除触发器。 */
const deleteResourceTrigger = (resource: ResourceTriggerResource, triggerId: string) => del<undefined, boolean>(`${getPrefix(resource)}/${triggerId}`)

export default { getResourceTriggerList, getResourceTriggerDetail, postResourceTrigger, putResourceTrigger, deleteResourceTrigger }
