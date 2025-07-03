import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
const ModelRouter = {
  path: '/tool',
  name: 'tool',
  meta: {
    title: 'views.tool.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.TOOL_READ.getWorkspacePermission,
      PermissionConst.TOOL_READ.getWorkspacePermissionWorkspaceManageRole,
    ],
    group: 'workspace',
    order: 3,
  },
  redirect: '/tool',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/tool',
      name: 'tool-index',
      meta: { title: '工具主页', activeMenu: '/tool' },
      sameRoute: 'tool',
      component: () => import('@/views/tool/index.vue'),
    },
  ],
}

export default ModelRouter
