import { PermissionConst, RoleConst } from '@/utils/permission/data'
const mindmapRouter = {
  path: '/mindmap',
  name: 'mindmap',
  meta: {
    title: '思维导图',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
    ],
    group: 'workspace',
    order: 2,
  },
  redirect: '/mindmap',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/mindmap',
      name: 'mindmap-index',
      meta: { title: '思维导图', activeMenu: '/mindmap', sameRoute: 'mindmap' },
      component: () => import('@/views/mindmap/index.vue'),
      hidden: true,
    },
  ],
}

export default mindmapRouter
