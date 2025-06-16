const ParagraphRouter = {
  path: '/paragraph/system/:id/:documentId/shared',
  name: 'ParagraphSharedSystem',
  meta: { title: 'common.fileUpload.document', activeMenu: '/knowledge', breadcrumb: true },
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  hidden: true,
  children: [
    {
      path: '/paragraph/system/:id/:documentId/shared',
      name: 'ParagraphIndexSharedSystem',
      meta: { activeMenu: '/knowledge' },
      component: () => import('@/views/shared/paragraph-shared/index.vue'),
    },
  ],
}

export default ParagraphRouter
