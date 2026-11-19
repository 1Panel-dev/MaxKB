import { computed, reactive } from 'vue'
import type { LoginMethod, RoleType } from '@/api/types'
import { LOGIN_METHOD, ROLE_TYPE } from '@/api/enums'
import { t } from '@/locales'

export const LOGIN_METHOD_LABELS = reactive({
  [LOGIN_METHOD.CAS]: computed(() => t('auth.methods.cas')),
  [LOGIN_METHOD.LDAP]: computed(() => t('auth.methods.ldap')),
  [LOGIN_METHOD.LOCAL]: computed(() => t('auth.methods.local')),
  [LOGIN_METHOD.OAUTH2]: computed(() => t('auth.methods.oauth2')),
  [LOGIN_METHOD.OIDC]: computed(() => t('auth.methods.oidc')),
  [LOGIN_METHOD.SAML2]: computed(() => t('auth.methods.saml2')),
  [LOGIN_METHOD.DINGTALK]: computed(() => t('auth.methods.dingtalk')),
  [LOGIN_METHOD.LARK]: computed(() => t('auth.methods.lark')),
  [LOGIN_METHOD.WECOM]: computed(() => t('auth.methods.wecom')),
} as const) satisfies Record<LoginMethod, string>

export const SCAN_FIELD_LABELS: Record<string, string> = {
  agent_id: 'Agent ID',
  app_key: 'App Key',
  app_secret: 'App Secret',
  corp_id: 'Corp ID',
}

export const ROLE_TYPE_LABELS: Record<RoleType, string> = reactive({
  [ROLE_TYPE.ADMIN]: computed(() => t('role.types.admin')),
  [ROLE_TYPE.WORKSPACE_MANAGE]: computed(() => t('role.types.workspaceAdmin')),
  [ROLE_TYPE.USER]: computed(() => t('role.types.user')),
})
