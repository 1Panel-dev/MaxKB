import { RoleTypeEnum } from '@/enums/system'
import type { FormItemRule } from 'element-plus'
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

interface CreateMemberParamsItem {
  user_ids: string[],
  workspace_ids: string[]
}

interface PageList<T> {
  current: number,
  size: number,
  total: number,
  records: T
}

type Arrayable<T> = T | T[]
interface FormItemModel {
  path: string
  label?: string
  rules?: Arrayable<FormItemRule>,
  selectProps: {
    options?: { label: string, value: string }[]
    placeholder?: string
  }
}

export type { RoleItem, FormItemModel, RolePermissionItem, RoleTableDataItem, CreateOrUpdateParams, PageList, ChildrenPermissionItem, RoleMemberItem, CreateMemberParamsItem }