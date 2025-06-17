const ModelRouter = {
  path: '/knowledge',
  name: 'knowledge',
  meta: { title: 'views.knowledge.title', permission: 'KNOWLEDGE:READ' },
  redirect: '/knowledge',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/knowledge',
      name: 'knowledge-index',
      meta: { title: '知识库主页', activeMenu: '/knowledge' },
      component: () => import('@/views/knowledge/index.vue'),
    },

    // 上传文档
    {
      path: '/knowledge/document/upload/:folderId',
      name: 'UploadDocument',
      meta: { activeMenu: '/knowledge' },
      component: () => import('@/views/document/UploadDocument.vue'),
      hidden: true,
    }
  ],
}

export default ModelRouter
