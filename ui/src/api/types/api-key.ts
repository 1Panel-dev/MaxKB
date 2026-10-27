/** 智能体与系统 API Key 共用的记录和修改参数。 */
export interface ApiKeyRecord {
  id: string
  secret_key: string
  is_active: boolean
  allow_cross_domain: boolean
  cross_domain_list: string[]
  is_permanent: boolean
  expire_time: string | null
  create_time?: string
  remark?: string | null
}

export interface ApiKeyPayload {
  is_active?: boolean
  allow_cross_domain?: boolean
  cross_domain_list?: string[]
  is_permanent?: boolean
  expire_time?: string | null
  remark?: string
}
