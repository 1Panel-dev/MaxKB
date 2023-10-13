const datasetRouter = {
  path: '/dataset',
  name: 'dataset',
  meta: { icon: 'app-dataset', title: '数据集', permission: 'DATASET:READ' },
  component: () => import('@/views/dataset/index.vue')
}

export default datasetRouter
