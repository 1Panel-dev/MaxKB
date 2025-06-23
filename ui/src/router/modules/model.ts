const ModelRouter = {
  path: '/model',
  name: 'model',
  meta: { title: 'views.model.title' },
  redirect: '/model',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/model',
      name: 'model-index',
      meta: { title: '模型主页', activeMenu: '/model' },
      component: () => import('@/views/model/index.vue')
    }
  ]
}

export default ModelRouter
