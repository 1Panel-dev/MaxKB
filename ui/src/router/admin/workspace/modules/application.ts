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
        component: () => import('@/views/application/index.vue'),
        meta: { title: '智能体列表', hidden: true },
      },
      {
        path: ':applicationId/:type',
        name: 'workspace-application-detail-layout',
        component: () => import('@/views/application-detail/index.vue'),
        meta: { title: '智能体详情', hidden: true, resourceDetailRoot: true },
        children: [
          {
            path: 'overview',
            name: 'workspace-application-overview',
            component: () => import('@/views/application-detail/overview/index.vue'),
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
            component: () => import('@/views/application-detail/setting/index.vue'),
            meta: {
              title: '设置',
              icon: 'icon_setting',
              activeIcon: 'icon_setting_filled',
              order: 20,
              detailMenuVisible: (params) => params.type === APPLICATION_TYPE.SIMPLE,
              canAccess: (params) => params.type === APPLICATION_TYPE.SIMPLE && perm.application.workspace.edit(String(params.applicationId)),
            },
          },
          {
            path: 'workflow-entry',
            name: 'workspace-application-workflow-setting',
            redirect: (to) => ({
              name: 'workflow-application',
              params: { workspaceId: to.params.workspaceId, applicationId: to.params.applicationId },
              query: to.query,
            }),
            meta: {
              title: '设置',
              icon: 'icon_setting',
              activeIcon: 'icon_setting_filled',
              order: 20,
              detailMenuVisible: (params) => params.type === APPLICATION_TYPE.WORK_FLOW,
              // 工作流跳转入口不能作为画布返回的落脚页。
              canAccess: () => false,
            },
          },
          {
            path: 'integration',
            name: 'workspace-application-integration',
            component: () => import('@/views/application-detail/integration/index.vue'),
            meta: { title: '接入第三方', icon: 'icon_dataset_outlined', activeIcon: 'icon_dataset_filled', order: 30 },
          },
          {
            path: 'chat-user',
            name: 'workspace-application-chat-user',
            component: () => import('@/views/application-detail/chat-user/index.vue'),
            meta: { title: '对话用户', icon: 'icon_contacts_outlined', activeIcon: 'icon_contacts_outlined', order: 40 },
          },
          {
            path: 'operation-log',
            name: 'workspace-application-operation-log',
            component: () => import('@/views/application-detail/operation-log/index.vue'),
            meta: { title: '操作日志', icon: 'icon_logs_outlined', activeIcon: 'icon_logs_filled', order: 50 },
          },
        ],
      },
    ],
  },
]
