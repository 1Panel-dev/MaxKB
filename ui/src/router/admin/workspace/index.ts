import type { RouteRecordRaw } from 'vue-router'
import { applicationRoutes } from './modules/application'
import { homeRoutes } from './modules/home'
import { knowledgeRoutes } from './modules/knowledge'
import { modelRoutes } from './modules/model'
import { toolRoutes } from './modules/tool'
import { triggerRoutes } from './modules/trigger'

/**
 * 工作空间路由只负责汇总模块。
 * 各模块的所有页面在 modules 内独立维护。
 */
const moduleRoutes: RouteRecordRaw[] = [
  ...homeRoutes,
  ...applicationRoutes,
  ...knowledgeRoutes,
  ...toolRoutes,
  ...modelRoutes,
  ...triggerRoutes,
  // {
  //   path: 'demo-dynamics-form',
  //   name: 'demo-dynamics-form',
  //   component: () => import('@/components/mk-dynamics-form/Demo.vue'),
  //   meta: { title: '动态表单演示' },
  // },
]

export const workspaceRoutes: RouteRecordRaw = {
  path: '/workspace/:workspaceId',
  component: () => import('@/layout/AppLayout.vue'),
  meta: { scope: 'workspace', resourceScope: 'workspace' },
  children: moduleRoutes,
}
