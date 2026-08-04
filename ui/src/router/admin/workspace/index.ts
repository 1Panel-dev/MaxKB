import type { RouteRecordRaw } from 'vue-router'
import { agentRoutes } from './modules/agent'
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
  ...agentRoutes,
  ...knowledgeRoutes,
  ...toolRoutes,
  ...modelRoutes,
  ...triggerRoutes,
]

export const workspaceRoutes: RouteRecordRaw = {
  path: '/workspace/:workspaceId',
  component: () => import('@/layout/AppLayout.vue'),
  meta: { scope: 'workspace' },
  children: moduleRoutes,
}
