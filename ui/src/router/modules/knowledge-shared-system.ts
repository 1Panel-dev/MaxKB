const ModelRouter = {
  path: '/knowledge/system',
  name: 'knowledgeSharedSystem',
  meta: { title: 'views.knowledge.title', permission: 'KNOWLEDGE:READ' },
  hidden: true,
  redirect: '/knowledge',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/knowledge/system/document/upload/shared',
      name: 'UploadDocumentSharedSystem',
      meta: { activeMenu: '/knowledge/system' },
      component: () => import('@/views/shared/document-shared/UploadDocument.vue'),
      hidden: true,
    },
    {
      path: '/knowledge/system/import/shared',
      name: 'ImportLarkDocumentShared',
      meta: { activeMenu: '/knowledge' },
      component: () => import('@/views/shared/document-shared/ImportLarkDocument.vue'),
      hidden: true,
    },
  ],
}

export default ModelRouter
