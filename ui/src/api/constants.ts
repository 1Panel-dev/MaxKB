/** Admin 与 Chat 的 API 部署路径配置。 */
const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '')

export const ADMIN_API_BASE_PATH = trimTrailingSlash(window.MaxKB?.prefix || import.meta.env.VITE_BASE_PATH || '/admin/') + '/api'

export const CHAT_API_BASE_PATH = trimTrailingSlash(window.MaxKB?.chatPrefix || import.meta.env.VITE_BASE_PATH || '/chat/') + '/api'
