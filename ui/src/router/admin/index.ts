import NProgress from 'nprogress'
import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '@/stores'
import { loginRoutes } from './login'
import { systemRoutes } from './system'
import { workspaceRoutes } from './workspace'
import { workflowRoutes } from './workflow'

const PUBLIC_ROUTE_NAMES = new Set(['login', 'forgot-password', 'not-found'])
const ADMIN_BASE_PATH = window.MaxKB?.prefix || import.meta.env.VITE_BASE_PATH || '/admin/'

NProgress.configure({
  minimum: 0.1,
  showSpinner: false,
  speed: 300,
  trickleSpeed: 200,
})

function getQueryToken(tokenQuery: unknown) {
  const token = Array.isArray(tokenQuery) ? tokenQuery[0] : tokenQuery
  return typeof token === 'string' ? token : undefined
}

const router = createRouter({
  history: createWebHistory(ADMIN_BASE_PATH),
  routes: [
    { path: '/', redirect: { name: 'workspace-home', params: { workspaceId: 'default' } } },
    ...loginRoutes,
    ...workflowRoutes,
    workspaceRoutes,
    systemRoutes,
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/error/NotFoundView.vue'),
      meta: { title: '页面不存在' },
    },
  ],
})

router.beforeEach((to) => {
  NProgress.start()

  const { login, platformInfo, theme, user } = useStore()
  const queryToken = getQueryToken(to.query.token)
  if (queryToken) {
    login.setToken(queryToken)
    const { token: _token, ...query } = to.query
    return {
      path: to.path,
      query,
      hash: to.hash,
      replace: true,
    }
  }

  const routeName = typeof to.name === 'string' ? to.name : ''
  if (PUBLIC_ROUTE_NAMES.has(routeName)) {
    return true
  }

  if (!login.isAuthenticated) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  return platformInfo
    .loadPlatformInfo()
    .then(
      () => {
        if (theme.isInitialized) return
        if (!platformInfo.isPremium) {
          theme.applyDefaultTheme()
          return
        }
        return theme.loadThemeInfo().then(undefined, () => theme.applyDefaultTheme())
      },
      () => theme.applyDefaultTheme(),
    )
    .then(() => {
      if (user.userInfo) return true
      return user.loadCurrentUser().then(
        () => true,
        () => {
          login.clearToken()
          return {
            name: 'login' as const,
            query: { redirect: to.fullPath },
          }
        },
      )
    })
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - MaxKB` : 'MaxKB'
  NProgress.done()
})

router.onError(() => {
  NProgress.done()
})

export default router
