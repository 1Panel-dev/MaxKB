/** 资源授权抽屉及其内部组件共用的展示类型。 */
import type { ResourceAuthorizationTargetType } from '@/api/types'
import type { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'

export type ResourcePermissionOption = (typeof RESOURCE_PERMISSION_OPTIONS)[number]

export interface ResourceAuthorizationContentProps {
  targetId: string
  type: ResourceAuthorizationTargetType
  isFolder: boolean
  isRootFolder?: boolean
  managedFolderIds: string[]
  editablePermissionOptions: ResourcePermissionOption[]
}
