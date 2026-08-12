export type AuthProviderType = 'LDAP' | 'CAS' | 'OIDC' | 'OAuth2' | 'SAML2'

export interface AuthProviderSetting {
  id?: string
  auth_type: AuthProviderType
  config: Record<string, string | boolean>
  is_active: boolean
}

export interface LoginMethodOption {
  label: string
  value: string
}

export interface LoginAuthSetting {
  auth_types?: LoginMethodOption[]
  default_value: string
  failed_attempts: number
  group_id?: string
  lock_time: number
  login_methods: string[]
  max_attempts: number
  permission?: string
  role_id?: string
  system_options?: LoginMethodOption[]
  workspace_id?: string
}

export type QrLoginPlatformType = 'wecom' | 'dingtalk' | 'lark'

export interface QrLoginPlatform {
  auth_type: QrLoginPlatformType
  config: Record<string, string>
  is_active: boolean
  is_valid: boolean
}

export interface QrLoginPlatformRequest {
  config: Record<string, string>
  isActive: boolean
  key: QrLoginPlatformType
}
