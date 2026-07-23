import { createRouter, createWebHistory } from 'vue-router'
import { loginRoutes } from './login'
import { systemRoutes } from './system'
import { workspaceRoutes } from './workspace'
import { workflowRoutes } from './workflow'

export type { RouteScope } from './types'

const TOKEN_KEY = 'access_token'

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_PATH || '/admin/'),
  routes: [
    { path: '/', redirect: { name: 'workspace-home' } },
    ...loginRoutes,
    ...workflowRoutes,
    workspaceRoutes,
    systemRoutes,
  ],
})

router.beforeEach((to) => {
  return true
})

router.afterEach((to) => {})

export default router
