/** 关联资源分页查询返回的资源关系及展示信息。 */
import type { ResourceType } from './resource-authorization'

export interface RelatedResource {
  id: string
  name: string | null
  desc?: string | null
  source_id: string
  source_type: ResourceType
  target_id: string
  target_type: ResourceType
  type?: string | null
  icon?: string | null
  username?: string | null
  workspace_id?: string | null
  workspace_name?: string | null
  folder_id?: string | null
}
