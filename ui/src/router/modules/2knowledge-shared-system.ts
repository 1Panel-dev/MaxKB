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
      meta: { activeMenu: '/knowledge1/system' },
      component: () => import('@/views/document-shared-system/UploadDocument.vue'),
      hidden: true,
    },
  ],
}

export default ModelRouter
