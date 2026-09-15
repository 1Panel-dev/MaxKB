import type { RouteRecordRaw } from 'vue-router'
import { perm } from '@/permission'
import { APPLICATION_TYPE } from '@/api/enums'

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
            name: 'workspace-application-overview',
            component: () => import('@/views/application-detail/overview/OverviewView.vue'),
            meta: {
              title: '概览',
              icon: 'icon_screen_outlined',
              activeIcon: 'icon_screen_filled',
              order: 10,
              canAccess: (params) => perm.application.workspace.overviewRead(String(params.applicationId)),
            },
          },
          {
            path: 'setting',
            name: 'workspace-application-simple-setting',
            component: () => import('@/views/application-detail/setting/SimpleSettingView.vue'),
            meta: {
              title: '设置',
              icon: 'icon_setting',
              activeIcon: 'icon_setting_filled',
              order: 20,
              canAccess: (params) => params.type === APPLICATION_TYPE.SIMPLE && perm.application.workspace.edit(String(params.applicationId)),
            },
          },
        ],
      },
    ],
  },
]
