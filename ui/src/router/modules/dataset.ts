import Layout from '@/layout/layout-template/DetailLayout.vue'
const datasetRouter = {
  path: '/dataset',
  name: 'dataset',
  meta: { title: 'views.dataset.title', permission: 'DATASET:READ' },
  component: () => import('@/layout/layout-template/AppLayout.vue'),
  redirect: '/dataset',
  children: [
    {
      path: '/dataset',
      name: 'dataset-index',
      meta: { title: '知识库主页', activeMenu: '/dataset' },
      component: () => import('@/views/dataset/index.vue')
    },
    {
      path: '/dataset/upload',
      name: 'UploadDocumentDataset',
      meta: { activeMenu: '/dataset' },
      component: () => import('@/views/dataset/UploadDocumentDataset.vue'),
      hidden: true
    },
    {
      path: '/dataset/:id',
      name: 'DatasetDetail',
      meta: { title: 'common.fileUpload.document', activeMenu: '/dataset' },
      component: Layout,
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
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/document/index.vue')
        },
        {
          path: 'problem',
          name: 'Problem',
          meta: {
            icon: 'app-problems',
            iconActive: 'QuestionFilled',
            title: 'views.problem.title',
            active: 'problem',
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/problem/index.vue')
        },
        {
          path: 'hit-test',
          name: 'DatasetHitTest',
          meta: {
            icon: 'app-hit-test',
            title: 'views.application.hitTest.title',
            active: 'hit-test',
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/hit-test/index.vue')
        },
        {
          path: 'setting',
          name: 'DatasetSetting',
          meta: {
            icon: 'app-setting',
            iconActive: 'app-setting-active',
            title: 'common.setting',
            active: 'setting',
            parentPath: '/dataset/:id',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/dataset/DatasetSetting.vue')
        }
      ]
    },
    {
      path: '/dataset/:id/:documentId', // 分段详情
      name: 'Paragraph',
      meta: { activeMenu: '/dataset' },
      component: () => import('@/views/paragraph/index.vue'),
      hidden: true
    },
    {
      path: '/dataset/import',
      name: 'ImportDocumentDataset',
      meta: { activeMenu: '/dataset' },
      component: () => import('@/views/dataset/ImportDocumentDataset.vue'),
      hidden: true
    },
  ]
}

export default datasetRouter
