/** 管理门户与单应用对话的浏览器存储 key，不包含语言缓存。 */
export const CHAT_STORAGE_KEY = {
  PORTAL_TOKEN: 'chat-portal-token',
} as const

/** 按单应用认证场景生成 token key。 */
export function getApplicationTokenStorageKey(scope: string) {
  return `chat-application-token-${scope}`
}

/** 按单应用访问标识生成用户表单 key；无标识时禁用缓存。 */
export function getUserFormStorageKey(accessToken: string) {
  return accessToken ? `${accessToken}userForm` : ''
}
