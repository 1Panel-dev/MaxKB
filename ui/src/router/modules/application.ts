import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
import { get_next_route } from '@/utils/permission'
const applicationRouter = {
  path: '/application',
  name: 'application',
  meta: {
    title: 'views.application.title',
    menu: true,
    permission: [
      RoleConst.ADMIN,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermissionWorkspaceManageRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermission,
    ],
    order: 1,
  },
  redirect: '/application',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/application',
      name: 'application-index',
      meta: { title: '应用主页', activeMenu: '/application' },
      component: () => import('@/views/application/index.vue'),
      hidden: true,
    },
  ],
}

export default applicationRouter
