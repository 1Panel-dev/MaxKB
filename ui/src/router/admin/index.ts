import NProgress from 'nprogress'
import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '@/stores'
import { loginRoutes } from './login'
import { systemRoutes } from './system'
import { workspaceRoutes } from './workspace'
import { workflowRoutes } from './workflow'

const ADMIN_BASE_PATH = window.MaxKB?.prefix || import.meta.env.VITE_BASE_PATH || '/admin/'

NProgress.configure({
  minimum: 0.3,
  showSpinner: false,
  speed: 500,
  trickleSpeed: 200,
})

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
    {
      path: '/demo/dynamics-form',
      name: '/demo-dynamics-form',
      component: () => import('@/components/mk-dynamics-form/Demo.vue'),
      meta: { title: '动态表单演示' },
    },
  ],
})

router.beforeEach(async (to) => {
  NProgress.start()
  const notAuthRouteNameList = ['login', 'forgot-password', 'not-found']
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
})

router.afterEach((to) => {
  NProgress.done()
})

router.onError(() => {
  NProgress.done()
})

export default router
