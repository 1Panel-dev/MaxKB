import type { RouteRecordRaw } from 'vue-router'

export const applicationRoutes: RouteRecordRaw[] = [
  {
    path: 'application',
    name: 'workspace-application',
    redirect: { name: 'workspace-application-list' },
    meta: { title: '智能体', activeMenu: 'workspace-application', icon: 'icon_robot_outlined', activeIcon: 'icon_robot_filled', order: 20 },
    children: [
      { path: '', name: 'workspace-application-list', component: () => import('@/views/application/ApplicationView.vue'), meta: { title: '智能体列表', hidden: true } },
      // {
      //   path: ':applicationId',
      //   name: 'workspace-application-detail',
      //   component: () => import('@/views/application/ApplicationDetailView.vue'),
      //   meta: { title: '智能体详情', hidden: true },
      // },
      // {
      //   path: ':applicationId/edit',
      //   name: 'workspace-application-edit',
      //   component: () => import('@/views/application/ApplicationDetailView.vue'),
      //   meta: { title: '编辑智能体', hidden: true },
      // },
    ],
  },
]
