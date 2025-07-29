import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
const ModelRouter = {
  path: '/knowledge',
  name: 'knowledge',
  meta: {
    title: 'views.knowledge.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.KNOWLEDGE_READ.getWorkspacePermission,
      PermissionConst.KNOWLEDGE_READ.getWorkspacePermissionWorkspaceManageRole,
    ],
    group: 'workspace',
    meta: { activeMenu: '/knowledge' },
    order: 2,
  },
  redirect: '/knowledge',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/knowledge',
      name: 'knowledge-index',
      meta: { title: '知识库主页', activeMenu: '/knowledge', sameRoute: 'knowledge' },
      component: () => import('@/views/knowledge/index.vue'),
    },

    // 上传文档
    {
      path: '/knowledge/document/upload/:folderId',
      name: 'UploadDocument',
      meta: { activeMenu: '/knowledge' },
      component: () => import('@/views/document/UploadDocument.vue'),
      hidden: true,
    },
    {
      path: '/knowledge/import/:folderId',
      name: 'ImportLarkDocument',
      meta: { activeMenu: '/knowledge' },
      component: () => import('@/views/document/ImportLarkDocument.vue'),
      hidden: true,
    },
  ],
}

export default ModelRouter
