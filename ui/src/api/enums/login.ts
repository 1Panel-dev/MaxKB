/** 后端登录方式枚举值；新增或修改登录方式时以此处为唯一数据源。 */
export const LOGIN_METHOD = {
  CAS: 'CAS',
  DINGTALK: 'dingtalk',
  LDAP: 'LDAP',
  LARK: 'lark',
  LOCAL: 'LOCAL',
  OAUTH2: 'OAuth2',
  OIDC: 'OIDC',
  SAML2: 'SAML2',
  WECOM: 'wecom',
} as const
