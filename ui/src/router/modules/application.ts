import { PermissionConst, RoleConst } from '@/utils/permission/data'
const applicationRouter = {
  path: '/application',
  name: 'application',
  meta: {
    title: 'views.application.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermissionWorkspaceManageRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermission,
    ],
    icon: 'app-agent',
    iconActive: 'app-agent-active',
    group: 'workspace',
    order: 1,
  },
  redirect: '/application',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/application',
      name: 'application-index',
      meta: { title: '智能体主页', activeMenu: '/application', sameRoute: 'application' },
      component: () => import('@/views/application/index.vue'),
      hidden: true,
    },
  ],
}

export default applicationRouter
