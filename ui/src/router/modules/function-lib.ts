import Layout from '@/layout/layout-template/DetailLayout.vue'
const functionLibRouter = {
  path: '/function-lib',
  name: 'function-lib',
  meta: { title: '函数库', permission: 'APPLICATION:READ' },
  redirect: '/function-lib',
  component: () => import('@/layout/layout-template/AppLayout.vue'),
  children: [
    {
      path: '/function-lib',
      name: 'function-lib',
      component: () => import('@/views/function-lib/index.vue')
    }
  ]
}

export default functionLibRouter
