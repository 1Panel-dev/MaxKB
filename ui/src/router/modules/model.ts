import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
const ModelRouter = {
  path: '/model',
  name: 'model',
  meta: {
    title: 'views.model.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.MODEL_READ.getWorkspacePermission,
      PermissionConst.MODEL_READ.getWorkspacePermissionWorkspaceManageRole,
    ],
    meta: { activeMenu: '/model' },
    group: 'workspace',
    order: 4,
  },
  redirect: '/model',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/model',
      name: 'model-index',
      meta: {
        title: '模型主页',
        activeMenu: '/model',
        sameRoute: 'model',
      },
      component: () => import('@/views/model/index.vue'),
    },
  ],
}

export default ModelRouter
