import { LOGIN_METHOD, ROLE_TYPE } from '@/api/enums'
import type { LoginMethod, RoleType } from '@/api/types'

export const LOGIN_METHOD_LABELS: Record<LoginMethod, string> = {
  [LOGIN_METHOD.CAS]: 'CAS',
  [LOGIN_METHOD.LDAP]: 'LDAP',
  [LOGIN_METHOD.LOCAL]: '账号登录',
  [LOGIN_METHOD.OAUTH2]: 'OAuth2',
  [LOGIN_METHOD.OIDC]: 'OIDC',
  [LOGIN_METHOD.SAML2]: 'SAML2',
  [LOGIN_METHOD.DINGTALK]: '钉钉',
  [LOGIN_METHOD.LARK]: '飞书',
  [LOGIN_METHOD.WECOM]: '企业微信',
}

export const SCAN_FIELD_LABELS: Record<string, string> = { agent_id: 'Agent ID', app_key: 'App Key', app_secret: 'App Secret', callback_url: '回调地址', corp_id: 'Corp ID' }

export const ROLE_TYPE_LABELS: Record<RoleType, string> = { [ROLE_TYPE.ADMIN]: '系统管理员', [ROLE_TYPE.WORKSPACE_MANAGE]: '工作空间管理员', [ROLE_TYPE.USER]: '普通用户' }
