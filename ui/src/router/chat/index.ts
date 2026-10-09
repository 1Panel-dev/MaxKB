import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router'
import { useStore } from '@/stores/chat'
import { PORTAL_AUTH_SCOPE } from '@/stores/chat/auth'
import type { AuthProfile } from '@/api/types'
import { chatRoutes } from './routes'

const CHAT_BASE_PATH = window.MaxKB?.prefix || import.meta.env.VITE_BASE_PATH || '/chat/'

const chatRouter = createRouter({ history: createWebHistory(CHAT_BASE_PATH), routes: chatRoutes })

const LOGIN_ROUTE_NAMES = new Set(['portal-login', 'chat-login'])

/** 根据路由得到认证场景：门户路由为门户场景，单应用路由为其 accessToken。 */
function getAuthScope(to: RouteLocationNormalized) {
  if (to.meta.portal) return PORTAL_AUTH_SCOPE

  const { accessToken } = to.params
  return typeof accessToken === 'string' && accessToken ? accessToken : undefined
}

/** `/portal` 下未定义的子路径会被单应用路由匹配为 accessToken = 'portal'。 */
function isUnknownPortalPath(to: RouteLocationNormalized) {
  return !to.meta.portal && to.params.accessToken === PORTAL_AUTH_SCOPE
}

function getLoginRoute(scope: string, to: RouteLocationNormalized) {
  const query = { redirect: to.fullPath }
  return scope === PORTAL_AUTH_SCOPE
    ? { name: 'portal-login', query }
    : { name: 'chat-login', params: { accessToken: scope }, query }
}

/** 渲染 404 页面并保留原地址，刷新时可重新尝试。 */
function getNotFoundRoute(to: RouteLocationNormalized) {
  return { name: 'chat-not-found', params: { pathMatch: to.path.substring(1).split('/') }, query: to.query, hash: to.hash }
}

chatRouter.beforeEach(async (to) => {
  if (isUnknownPortalPath(to)) return { name: 'portal-home', replace: true }

  const scope = getAuthScope(to)
  if (!scope) return true

  const { auth } = useStore()

  // accessToken 无效、应用已停用或门户未开放时，认证前置配置与匿名认证会失败，统一进入 404 页面
  let authProfile: AuthProfile<unknown>
  try {
    authProfile = await auth.fetchAuthProfile(scope)
  } catch {
    return getNotFoundRoute(to)
  }

  // 判断时只读取目标场景已保存的 token，放行前再切换当前场景，避免导航未完成时请求带上目标场景的 token
  if (LOGIN_ROUTE_NAMES.has(String(to.name)) || auth.getStoredToken(scope)) {
    auth.activate(scope, authProfile)
    return true
  }

  if (!authProfile.enable_auth) {
    try {
      await auth.postAnonymousAuth(scope)
    } catch {
      return getNotFoundRoute(to)
    }
    auth.activate(scope, authProfile)
    return true
  }

  return getLoginRoute(scope, to)
})

chatRouter.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - MaxKB` : 'MaxKB'
})

let isReauthenticating = false

/**
 * token 失效（401）时将当前场景的 token 标记为失效，并重新导航到当前地址，由守卫决定匿名认证或跳转登录页。
 * 同一时间只处理一次，避免并发请求重复触发导航。
 */
export function reauthenticate() {
  if (isReauthenticating) return

  isReauthenticating = true
  useStore().auth.expireToken()
  chatRouter.replace({ path: chatRouter.currentRoute.value.fullPath, force: true }).finally(() => {
    isReauthenticating = false
  })
}

export default chatRouter
