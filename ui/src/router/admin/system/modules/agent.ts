import type { RouteRecordRaw } from 'vue-router'

/** System 来源的智能体详情路由，与 Workspace 复用页面组件。 */
export const systemAgentRoutes: RouteRecordRaw[] = [
  {
    path: 'agent/:agentId',
    name: 'system-agent-detail',
    component: () => import('@/views/agent/AgentDetailView.vue'),
    meta: { title: '智能体详情', hidden: true },
  },
  {
    path: 'agent/:agentId/edit',
    name: 'system-agent-edit',
    component: () => import('@/views/agent/AgentDetailView.vue'),
    meta: { title: '编辑智能体', hidden: true },
  },
]
