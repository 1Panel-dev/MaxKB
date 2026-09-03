import type { RouteRecordRaw } from 'vue-router'

/** 各业务 Workflow 使用独立的全屏画布，不挂载 Workspace 或 System Layout。 */
export const workflowRoutes: RouteRecordRaw[] = [
  {
    path: '/workspace/:workspaceId/application/:applicationId/workflow',
    name: 'workflow-application',
    component: () => import('@/views/workflow/ApplicationWorkflowView.vue'),
    meta: { title: '智能体工作流' },
  },
  {
    path: '/workspace/:workspaceId/tool/:toolId/workflow',
    name: 'workflow-tool',
    component: () => import('@/views/workflow/ToolWorkflowView.vue'),
    meta: { title: '工具工作流' },
  },
]
