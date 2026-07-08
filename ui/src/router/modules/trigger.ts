import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
const ModelRouter = {
  path: '/trigger',
  name: 'trigger',
  meta: {
    title: 'views.trigger.title',
    permission: [
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.TRIGGER_READ.getWorkspacePermissionWorkspaceManageRole,
    ],
    group: 'workspace',
    order: 5,
  },
  hidden: true,
  redirect: '/trigger',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/trigger',
      name: 'trigger-index',
      meta: { title: '触发器主页', activeMenu: '/trigger' },
      sameRoute: 'trigger',
      component: () => import('@/views/trigger/index.vue'),
    },
  ],
}

export default ModelRouter
