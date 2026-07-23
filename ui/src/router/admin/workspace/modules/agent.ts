import type { RouteRecordRaw } from 'vue-router'

export const agentRoutes: RouteRecordRaw[] = [
  {
    path: 'agent',
    name: 'workspace-agent',
    redirect: { name: 'workspace-agent-list' },
    meta: { title: '智能体', icon: 'icon_magic_stick_outlined', order: 20 },
    children: [
      {
        path: '',
        name: 'workspace-agent-list',
        component: () => import('@/views/home/HomeView.vue'),
        meta: { title: '智能体列表', hidden: true },
      },
      {
        path: ':agentId',
        name: 'workspace-agent-detail',
        component: () => import('@/views/agent/AgentDetailView.vue'),
        meta: { title: '智能体详情', hidden: true },
      },
      {
        path: ':agentId/edit',
        name: 'workspace-agent-edit',
        component: () => import('@/views/agent/AgentDetailView.vue'),
        meta: { title: '编辑智能体', hidden: true },
      },
    ],
  },
]
