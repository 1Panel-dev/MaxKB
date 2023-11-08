import Layout from '@/layout/main-layout/index.vue'
const datasetRouter = {
  path: '/dataset',
  name: 'dataset',
  meta: { icon: 'app-dataset', title: '数据集', permission: 'DATASET:READ' },
  redirect: '/dataset',
  children: [
    {
      path: '/dataset',
      name: 'dataset',
      component: () => import('@/views/dataset/index.vue')
    },
    {
      path: '/dataset/:type', // create 或者 upload
      name: 'CreateDataset',
      meta: { activeMenu: '/dataset' },
      component: () => import('@/views/dataset/CreateDataset.vue'),
      hidden: true
    },
    {
      path: '/dataset/:datasetId',
      name: 'DatasetDetail',
      meta: { title: '文档', activeMenu: '/dataset' },
      component: Layout,
      hidden: true,
      children: [
        {
          path: 'document',
          name: 'DatasetDocument',
          meta: {
            icon: 'Document',
            title: '文档',
            active: 'document',
            parentPath: '/dataset/:datasetId',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/dataset/DatasetDocument.vue')
        },
        {
          path: 'setting',
          name: 'DatasetSetting',
          meta: {
            icon: 'Setting',
            title: '设置',
            active: 'setting',
            parentPath: '/dataset/:datasetId',
            parentName: 'DatasetDetail'
          },
          component: () => import('@/views/dataset/DatasetSetting.vue')
        }
      ]
    }
  ]
}

export default datasetRouter
