/** 资源授权抽屉及其内部组件共用的展示类型。 */
import type { RESOURCE_PERMISSION_OPTIONS } from '@/constants/resource-authorization'

export type ResourcePermissionOption = (typeof RESOURCE_PERMISSION_OPTIONS)[number]
