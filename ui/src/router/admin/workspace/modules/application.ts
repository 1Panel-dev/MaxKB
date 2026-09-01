import type { RouteRecordRaw } from 'vue-router'

export const applicationRoutes: RouteRecordRaw[] = [
  {
    path: 'application',
    name: 'workspace-application',
    redirect: { name: 'workspace-application-list' },
    meta: { title: '智能体', activeMenu: 'workspace-application', icon: 'icon_robot_outlined', activeIcon: 'icon_robot_filled', order: 20 },
    children: [
      {
        path: '',
        name: 'workspace-application-list',
        component: () => import('@/views/application/ApplicationView.vue'),
        meta: { title: '智能体列表', hidden: true },
      },
      {
        path: ':applicationId/:type',
        name: 'workspace-application-detail-layout',
        component: () => import('@/views/application-detail/WorkspaceApplicationDetail.vue'),
        meta: { title: '智能体详情', hidden: true },
        children: [
          {
            path: 'overview',
            name: 'workspace-application-detail',
            component: () => import('@/views/application-detail/overview/OverviewView.vue'),
            meta: { title: '概览', icon: 'icon_screen_outlined', activeIcon: 'icon_screen_filled', order: 10 },
          },
          {
            path: 'setting',
            name: 'workspace-application-simple-setting',
            component: () => import('@/views/application-detail/setting/SimpleSettingView.vue'),
            meta: { title: '设置', icon: 'icon-setting', activeIcon: 'icon_setting_filled', order: 20 },
          },
        ],
      },
    ],
  },
]
