/** 集中管理 Admin 的浏览器存储 key，保留已有值以兼容本地数据。 */

export const ADMIN_STORAGE_KEY = {
  TOKEN: 'token',
  WORKSPACE_ID: 'workspaceId',
  LANGUAGE: 'MaxKB-locale',
  PROMPT_CACHE: 'PROMPT_CACHE',
} as const
