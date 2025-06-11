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

interface RoleMemberItem {
  user_relation_id: string,
  user_id: string,
  username: string,
  nick_name: string,
  workspace_id: string,
  workspace_name: string,
}

interface CreateMemberParams {
  members: { user_ids: string[], workspace_ids: string[] }[]
}

export type { RoleItem, RolePermissionItem, RoleTableDataItem, CreateOrUpdateParams, ChildrenPermissionItem, RoleMemberItem, CreateMemberParams }