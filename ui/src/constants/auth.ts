import type { LoginMethod } from '@/api/types'

export const LOGIN_METHOD_LABELS: Record<LoginMethod, string> = {
  CAS: 'CAS',
  LDAP: 'LDAP',
  LOCAL: '账号登录',
  OAuth2: 'OAuth2',
  OIDC: 'OIDC',
  SAML2: 'SAML2',
  dingtalk: '钉钉',
  lark: '飞书',
  wecom: '企业微信',
}

export const SCAN_FIELD_LABELS: Record<string, string> = {
  agent_id: 'Agent ID',
  app_key: 'App Key',
  app_secret: 'App Secret',
  callback_url: '回调地址',
  corp_id: 'Corp ID',
}
