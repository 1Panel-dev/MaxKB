const ModelRouter = {
  path: '/knowledge/:id',
  name: 'DatasetDetail',
  meta: { title: 'common.fileUpload.document', activeMenu: '/knowledge', breadcrumb: true },
  component: () => import('@/layout/layout-template/MainLayout.vue'),
  hidden: true,
  children: [
    {
      path: 'document',
      name: 'Document',
      meta: {
        icon: 'app-document',
        iconActive: 'app-document-active',
        title: 'common.fileUpload.document',
        active: 'document',
        parentPath: '/knowledge/:id',
        parentName: 'DatasetDetail',
      },
      component: () => import('@/views/document/index.vue'),
    },
    // {
    //   path: 'problem',
    //   name: 'Problem',
    //   meta: {
    //     icon: 'app-problems',
    //     iconActive: 'QuestionFilled',
    //     title: 'views.problem.title',
    //     active: 'problem',
    //     parentPath: '/dataset/:id',
    //     parentName: 'DatasetDetail'
    //   },
    //   component: () => import('@/views/problem/index.vue')
    // },
    // {
    //   path: 'hit-test',
    //   name: 'DatasetHitTest',
    //   meta: {
    //     icon: 'app-hit-test',
    //     title: 'views.application.hitTest.title',
    //     active: 'hit-test',
    //     parentPath: '/dataset/:id',
    //     parentName: 'DatasetDetail'
    //   },
    //   component: () => import('@/views/hit-test/index.vue')
    // },
    // {
    //   path: 'setting',
    //   name: 'DatasetSetting',
    //   meta: {
    //     icon: 'app-setting',
    //     iconActive: 'app-setting-active',
    //     title: 'common.setting',
    //     active: 'setting',
    //     parentPath: '/dataset/:id',
    //     parentName: 'DatasetDetail'
    //   },
    //   component: () => import('@/views/dataset/DatasetSetting.vue')
    // }
  ],
}

export default ModelRouter
