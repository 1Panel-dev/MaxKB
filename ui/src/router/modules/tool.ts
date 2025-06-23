const ModelRouter = {
  path: '/tool',
  name: 'tool',
  meta: { title: 'views.tool.title' },
  redirect: '/tool',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/tool',
      name: 'tool-index',
      meta: { title: '工具主页', activeMenu: '/tool' },
      component: () => import('@/views/tool/index.vue')
    }
  ]
}

export default ModelRouter
