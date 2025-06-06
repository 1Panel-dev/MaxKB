const ParagraphRouter = {
  path: '/paragraph/:id/:documentId',
  name: 'Paragraph',
  meta: { title: 'common.fileUpload.document', activeMenu: '/knowledge', breadcrumb: true },
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  hidden: true,
  children: [
    {
      path: '/paragraph/:id/:documentId',
      name: 'ParagraphIndex',
      meta: { activeMenu: '/knowledge' },
      component: () => import('@/views/paragraph/index.vue'),
    },
  ],
}

export default ParagraphRouter
