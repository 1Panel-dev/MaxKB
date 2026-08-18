import type { RouteRecordRaw } from 'vue-router'

/** 各业务 Workflow 使用独立的全屏画布，不挂载 Workspace 或 System Layout。 */
export const workflowRoutes: RouteRecordRaw[] = [
  {
    path: '/workflow/agent/:agentId',
    name: 'workflow-agent',
    component: () => import('@/views/workflow/AgentWorkflowView.vue'),
    props: true,
    meta: { title: '智能体工作流' },
  },
]
