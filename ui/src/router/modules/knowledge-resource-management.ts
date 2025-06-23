const ModelRouter = {
  path: '/knowledge/resource-management',
  name: 'knowledgeResourceManagement',
  meta: { title: 'views.knowledge.title', permission: 'KNOWLEDGE:READ' },
  hidden: true,
  redirect: '/knowledge',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [

    {
      path: '/knowledge/resource-management/document/upload',
      name: 'UploadDocumentResourceManagement',
      meta: { activeMenu: '/knowledge/resource' },
      component: () => import('@/views/resource-management/document/UploadDocument.vue'),
      hidden: true,
    },
  ],
}

export default ModelRouter
