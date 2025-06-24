import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
const ModelRouter = {
  path: '/model',
  name: 'model',
  meta: {
    title: 'views.model.title',
    menu: true,
    permission: [
      RoleConst.ADMIN,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.MODEL_READ.getWorkspacePermission,
      PermissionConst.MODEL_READ.getWorkspacePermissionWorkspaceManageRole,
    ],
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
      },
      component: () => import('@/views/model/index.vue'),
    },
  ],
}

export default ModelRouter
