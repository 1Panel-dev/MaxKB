import NProgress from 'nprogress'
import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalizedLoaded,
  type RouteLocationNormalized,
  type RouteLocationResolvedGeneric,
} from 'vue-router'
import { useStore } from '@/stores'
import { loginRoutes } from './login'
import { systemRoutes } from './system'
import { workspaceRoutes } from './workspace'
import { workflowRoutes } from './workflow'
import { getChildRouteList } from './utils'
const ADMIN_BASE_PATH = window.MaxKB?.prefix || import.meta.env.VITE_BASE_PATH || '/admin/'

NProgress.configure({ minimum: 0.3, showSpinner: false, speed: 500, trickleSpeed: 200 })

const router = createRouter({
  history: createWebHistory(ADMIN_BASE_PATH),
  routes: [
    { path: '/', redirect: { name: 'workspace-home', params: { workspaceId: 'default' } } },
    // (demo): 执行详情样式预览，不涉及权限，不加入权限路由
    { path: '/details-demo', name: 'details-demo', component: () => import('@/views/details-demo/index.vue'), meta: { title: '执行详情 Demo' } },
    ...loginRoutes,
    ...workflowRoutes,
    workspaceRoutes,
    systemRoutes,
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/error/index.vue'), meta: { title: '页面不存在' } },
  ],
})

router.beforeEach(async (to, from) => {
  if (to.path !== from.path) NProgress.start()
  const notAuthRouteNameList = ['login', 'forgot-password', 'not-found', 'details-demo']
  const { auth, user } = useStore()

  if (!notAuthRouteNameList.includes(to.name ? to.name.toString() : '')) {
    if (to.query && to.query.token) {
      auth.setToken(to.query.token.toString())
    }
    if (!auth.isAuthenticated) {
      auth.clearToken()
      return { name: 'login', query: { redirect: to.fullPath, client: to.query.client, corpId: to.query.corpId } }
    }
    if (!user.userInfo) {
      await auth.loadAuthBaseProfile()
    }

    // 用户只属于部分工作空间时，自动落到其首个可访问工作空间；
    // 避免登录/根路径/返回等入口硬编码进入 default 而出现选中为空、无权限。
    const workspaceId = to.params?.workspaceId as string | undefined
    const workspace_list = user.userInfo?.workspace_list
    if (to.name && workspaceId && workspace_list?.length) {
      const accessibleIds = new Set(workspace_list.map((ws) => ws.id).filter((id): id is string => Boolean(id)))
      if (!accessibleIds.has(workspaceId)) {
        const fallbackId = workspace_list.find((ws) => ws.id)?.id ?? 'default'
        if (fallbackId !== workspaceId) {
          return { name: to.name, params: { ...to.params, workspaceId: fallbackId }, replace: true }
        }
      }
    }
  }

const workspaceList = user.userInfo?.workspace_list ?? []
if (to.name === 'workspace-home' && workspaceList.length === 0) {
  const hasSystemAccess = getChildRouteList('system').some((item) => (item.permission ? item.permission() : true))
  if (hasSystemAccess) {
    return { name: 'system-home', replace: true }
  }
  // 没有任何工作空间、也没有系统权限：不做额外处理，保持原有行为
}

  // 当前路由有权限，放行
  if (!to.meta?.permission || (to.meta.permission as (route: RouteLocationNormalizedLoaded) => boolean)(to)) {
    return true
  }

  // 当前没权限，沿 next 找
  const visited = new Set()
  let currentName = to.name ? to.name.toString() : ''

  while (currentName) {
    if (visited.has(currentName)) {
      return { name: 'no-permission', replace: true }
    }
    visited.add(currentName)

    const currentRoute = router.resolve({ name: currentName, params: to.params })
    const nextName = currentRoute?.meta?.next as string

    if (!nextName) {
      return { name: 'no-permission', replace: true }
    }

    const nextRoute = router.resolve({ name: nextName, params: to.params })
    if (nextRoute?.name) {
      const nextPermission = nextRoute.meta?.permission as (
        route?: RouteLocationNormalized | RouteLocationResolvedGeneric | RouteLocationNormalizedLoaded,
      ) => boolean
      if (!nextPermission || nextPermission(nextRoute)) {
        return { name: nextName, params: to.params, query: to.query, hash: to.hash, replace: true }
      }
    }

    currentName = nextName
  }
  return { name: 'no-permission', replace: true }
})

router.afterEach((to) => {
  NProgress.done()
})

router.onError(() => {
  NProgress.done()
})

export default router
