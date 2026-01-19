import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
const ModelRouter = {
  path: '/trigger',
  name: 'trigger',
  meta: {
    title: 'views.trigger.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.TOOL_READ.getWorkspacePermission,
      PermissionConst.TOOL_READ.getWorkspacePermissionWorkspaceManageRole,
    ],
    icon: 'app-tool',
    iconActive: 'app-tool-active',
    group: 'workspace',
    order: 5,
  },
  redirect: '/trigger',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/trigger',
      name: 'trigger-index',
      meta: { title: '工具主页', activeMenu: '/trigger' },
      sameRoute: 'trigger',
      component: () => import('@/views/trigger/index.vue'),
    },
  ],
}

export default ModelRouter
