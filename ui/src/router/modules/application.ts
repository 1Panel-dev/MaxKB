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
    group: 'workspace',
    order: 1,
  },
  redirect: '/application',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/application',
      name: 'application-index',
      meta: { title: '应用主页', activeMenu: '/application', sameRoute: 'application' },
      component: () => import('@/views/application/index.vue'),
      hidden: true,
    },
  ],
}

export default applicationRouter
