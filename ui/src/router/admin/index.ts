import NProgress from 'nprogress'
import { createRouter, createWebHistory , type RouteLocationNormalizedLoaded,type RouteLocationNormalized,type RouteLocationResolvedGeneric} from 'vue-router'
import { useStore } from '@/stores'
import { loginRoutes } from './login'
import { systemRoutes } from './system'
import { workspaceRoutes } from './workspace'
import { workflowRoutes } from './workflow'
const ADMIN_BASE_PATH = window.MaxKB?.prefix || import.meta.env.VITE_BASE_PATH || '/admin/'

NProgress.configure({ minimum: 0.3, showSpinner: false, speed: 500, trickleSpeed: 200 })

const router = createRouter({
  history: createWebHistory(ADMIN_BASE_PATH),
  routes: [
    { path: '/', redirect: { name: 'workspace-home', params: { workspaceId: 'default' } } },
    // TODO(demo): 执行详情样式预览，验收后删除
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
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    if (!user.userInfo) {
      await auth.loadAuthBaseProfile()
    }
  }

  // 当前路由有权限，放行
  if (!to.meta?.permission || (to.meta.permission as (route:RouteLocationNormalizedLoaded)=>boolean)(to)) {
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

    const currentRoute = router.resolve({ name: currentName })
    const nextName = currentRoute?.meta?.next as string

    if (!nextName) {
      return { name: 'no-permission', replace: true }
    }

    const nextRoute = router.resolve({ name: nextName })
    if (nextRoute?.name) {
      const nextPermission = nextRoute.meta?.permission as ((route?:RouteLocationNormalized |RouteLocationResolvedGeneric| RouteLocationNormalizedLoaded)=>boolean)
      if (!nextPermission || nextPermission(nextRoute)) {
        return { name: nextName, replace: true }
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
