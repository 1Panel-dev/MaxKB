import type { LoginMethod, RoleType } from '@/api/types'
import { LOGIN_METHOD, ROLE_TYPE } from '@/api/enums'

export const LOGIN_METHOD_LABEL_KEYS = {
  [LOGIN_METHOD.CAS]: 'auth.methods.cas',
  [LOGIN_METHOD.LDAP]: 'auth.methods.ldap',
  [LOGIN_METHOD.LOCAL]: 'auth.methods.local',
  [LOGIN_METHOD.OAUTH2]: 'auth.methods.oauth2',
  [LOGIN_METHOD.OIDC]: 'auth.methods.oidc',
  [LOGIN_METHOD.SAML2]: 'auth.methods.saml2',
  [LOGIN_METHOD.DINGTALK]: 'auth.methods.dingtalk',
  [LOGIN_METHOD.LARK]: 'auth.methods.lark',
  [LOGIN_METHOD.WECOM]: 'auth.methods.wecom',
} as const satisfies Record<LoginMethod, string>

export const SCAN_FIELD_LABELS: Record<string, string> = {
  agent_id: 'Agent ID',
  app_key: 'App Key',
  app_secret: 'App Secret',
  corp_id: 'Corp ID',
}

export const ROLE_TYPE_MESSAGE_KEYS: Record<RoleType, string> = {
  [ROLE_TYPE.ADMIN]: 'role.types.admin',
  [ROLE_TYPE.WORKSPACE_MANAGE]: 'role.types.workspaceAdmin',
  [ROLE_TYPE.USER]: 'role.types.user',
}
