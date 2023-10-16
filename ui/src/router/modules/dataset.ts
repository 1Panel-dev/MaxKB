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
      path: '/dataset/doc',
      name: 'DatasetDoc',
      meta: { icon: 'House', title: '文档', activeMenu: '/dataset' },
      component: Layout,
      hidden: true,
      redirect: '/dataset/doc',
      children: [
        {
          path: '/dataset/doc',
          name: 'DatasetDoc',
          meta: { icon: 'House', title: '文档' },
          component: () => import('@/views/dataset/DatasetDoc.vue')
        }
      ]
    }
  ]
}

export default datasetRouter
