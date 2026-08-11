export interface RoleItem {
  id: string
  role_name: string
  type: string
  internal: boolean
  user_count?: number
}

export interface RolePermissionItem {
  id: string
  name: string
  children: {
    id: string
    name: string
    permission: { id: string; name: string; enable: boolean }[]
    enable: boolean
  }[]
}

export interface RoleTableDataItem {
  module: string
  name: string
  permission: { id: string; name: string; enable: boolean }[]
  enable: boolean
  perChecked: string[]
  indeterminate: boolean
}

export interface RoleMemberItem {
  user_relation_id: string
  user_id: string
  username: string
  nick_name: string
  workspace_name?: string
}

export interface FormItemModel {
  path: string
  label?: string
  rules?: any[]
  hidden?: (model: any) => boolean
  selectProps?: {
    options?: { label: string; value: string }[]
    placeholder?: string
    multiple?: boolean
    remoteMethod?: (query: string, element: any) => Promise<any[]>
  }
}
