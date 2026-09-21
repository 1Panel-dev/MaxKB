import type { Dict } from './common'

export interface PortalAuthConfig extends Dict<unknown> {
  login_value?: string[]
  default_value?: string
  max_attempts?: number
  failed_attempts?: number
  lock_time?: number
}

export interface PortalSetting {
  id: string
  name: string
  description: string | null
  logo: string | null
  tab_logo: string | null
  enable_public_access: boolean
  enable_api: boolean
  enable_knowledge_base_api: boolean
  enable_auth: boolean
  auth_config: PortalAuthConfig
  enable_cors: boolean
  cors_config: Dict<unknown>
}

export type PortalSettingPayload = Partial<Omit<PortalSetting, 'id'>>
