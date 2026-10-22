/** System 共享资源授权 API 与页面共用的业务类型。 */
import type { RESOURCE_TYPE } from '@/api/enums'
import type { ResourceType } from './resource-authorization'

export type SharedResourceType = Exclude<ResourceType, typeof RESOURCE_TYPE.APPLICATION>

export interface SharedWorkspaceAuthorization {
  authentication_type: 'WHITE_LIST' | 'BLACK_LIST'
  workspace_id_list: string[]
}
