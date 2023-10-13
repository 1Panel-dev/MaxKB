const applicationRouter = {
  path: '/app',
  name: 'app',
  meta: { icon: 'app-applicaiton', title: '应用', permission: 'APPLICATION:READ' },
  component: () => import('@/views/app/index.vue')
}

export default applicationRouter
