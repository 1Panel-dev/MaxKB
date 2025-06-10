import { RoleTypeEnum } from '@/enums/system'

interface RoleItem {
  id: string,
  role_name: string,
  type: RoleTypeEnum,
  create_user: string,
  internal: boolean,
}

interface ChildrenPermissionItem {
  id: string
  name: string
  enable: boolean
}

interface RolePermissionItem {
  id: string,
  name: string,
  children: {
    id: string,
    name: string,
    permission: ChildrenPermissionItem[],
    enable: boolean,
  }[]
}

interface RoleTableDataItem {
  module: string
  name: string
  permission: ChildrenPermissionItem[]
  enable: boolean
  perChecked: string[]
  indeterminate: boolean
}

interface CreateOrUpdateParams {
  role_id?: string,
  role_name: string,
  role_type?: RoleTypeEnum,
}

export type { RoleItem, RolePermissionItem, RoleTableDataItem, CreateOrUpdateParams, ChildrenPermissionItem }