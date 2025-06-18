const ParagraphRouter = {
  path: '/paragraph/resource/:id/:documentId/management',
  name: 'ParagraphResourceManagement',
  meta: { title: 'common.fileUpload.document', activeMenu: '/knowledge', breadcrumb: true },
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  hidden: true,
  children: [
    {
      path: '/paragraph/resource/:id/:documentId/management',
      name: 'ParagraphIndexResourceManagement',
      meta: { activeMenu: '/knowledge' },
      component: () => import('@/views/resource-management/paragraph/index.vue'),
    },
  ],
}

export default ParagraphRouter
