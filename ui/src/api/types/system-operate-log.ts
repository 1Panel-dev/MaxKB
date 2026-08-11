import type { RequestParams } from './common'

export interface OperateLogUser {
  email?: string
  username?: string
}

export interface OperateLog {
  id: string
  create_time: string
  details?: unknown
  ip_address: string
  menu: string
  operate: string
  operation_object?: { name?: string }
  status: number
  user?: OperateLogUser
  workspace_name?: string
}

export interface OperateLogMenuOption {
  menu: string
  menu_label: string
}

export interface OperateLogQuery extends RequestParams {
  end_time?: string
  ip_address?: string
  menu?: string
  start_time?: string
  status?: string
  user?: string
  workspace_ids?: string
}
