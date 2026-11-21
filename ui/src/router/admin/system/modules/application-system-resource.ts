import type { RouteRecordRaw } from 'vue-router'
import { APPLICATION_TYPE } from '@/api/enums'
import { perm } from '@/permission'

/** System 资源管理智能体详情，与 Workspace 复用页面，不提供共享详情。 */
export const systemResourceApplicationRoutes: RouteRecordRaw[] = [
  {
    path: '/system/resource/application/:applicationId/:type',
    name: 'system-resource-application-detail',
    component: () => import('@/views/application-detail/index.vue'),
    redirect: { name: 'system-resource-application-overview' },
    meta: {
      title: '智能体详情',
      hidden: true,
      resourceDetailRoot: true,
      activeMenu: '/system/resource/applications',
      scope: 'system',
      resourceScope: 'system-resource',
    },
    children: [
      {
        path: 'overview',
        name: 'system-resource-application-overview',
        component: () => import('@/views/application-detail/overview/index.vue'),
        meta: {
          title: 'overview.title',
          icon: 'icon_screen_outlined',
          activeIcon: 'icon_screen_filled',
          order: 10,
          canAccess: () => perm.application.system.overviewRead(),
          permission: () => perm.application.system.overviewRead(),
          next: 'system-resource-application-workflow-setting',
        },
      },
      {
        path: 'setting',
        name: 'system-resource-application-simple-setting',
        component: () => import('@/views/application-detail/setting/index.vue'),
        meta: {
          title: 'common.labels.settings',
          icon: 'icon_setting',
          activeIcon: 'icon_setting_filled',
          order: 20,
          detailMenuVisible: (params) => params.type === APPLICATION_TYPE.SIMPLE,
          canAccess: (params) => params.type === APPLICATION_TYPE.SIMPLE && perm.application.system.edit(),
          permission: () => perm.application.system.edit(),
          next: 'system-resource-application-access',
        },
      },
      {
        path: 'workflow-entry',
        name: 'system-resource-application-workflow-setting',
        redirect: (to) => ({
          name: 'system-resource-workflow-application',
          params: { applicationId: to.params.applicationId },
          query: to.query,
        }),
        meta: {
          title: 'common.labels.settings',
          icon: 'icon_setting',
          activeIcon: 'icon_setting_filled',
          order: 20,
          detailMenuVisible: (params) => params.type === APPLICATION_TYPE.WORK_FLOW,
          // 工作流跳转入口不能作为画布返回的落脚页。
          canAccess: () => false,
        },
      },
      {
        path: 'access',
        name: 'system-resource-application-access',
        component: () => import('@/views/application-detail/access/index.vue'),
        meta: {
          title: 'application.access.title',
          icon: 'icon_application_outlined',
          activeIcon: 'icon_application_filled',
          order: 30,
          permission: () => perm.application.system.accessRead(),
          next: 'system-resource-application-chat-user',
        },
      },
      {
        path: 'chat-user',
        name: 'system-resource-application-chat-user',
        component: () => import('@/views/application-detail/chat-user/index.vue'),
        meta: {
          title: 'authorization.chatUserTitle',
          icon: 'icon_contacts_outlined',
          activeIcon: 'icon_contacts_filled',
          order: 40,
          permission: () => perm.application.system.chatUserRead(),
          next: 'system-resource-application-operation-log',
        },
      },
      {
        path: 'operation-log',
        name: 'system-resource-application-operation-log',
        component: () => import('@/views/application-detail/chat-log/index.vue'),
        meta: {
          title: 'application.chatLog.title',
          icon: 'icon_logs_outlined',
          activeIcon: 'icon_logs_filled',
          order: 50,
          permission: () => perm.application.system.chatLogRead(),
          next: 'system-resource-application-overview',
        },
      },
    ],
  },
]
