import type { RouteRecordRaw } from 'vue-router'

/** Workflow 使用独立的全屏编排界面，不挂载工作空间侧栏。 */
export const workflowRoutes: RouteRecordRaw[] = [
  {
    path: '/workflow/:id',
    name: 'workflow-editor',
    component: () => import('@/views/workflow/WorkflowView.vue'),
    meta: { title: '工作流编排' },
  },
  // 调试、运行记录等页面继续在此模块中扩展。
]
