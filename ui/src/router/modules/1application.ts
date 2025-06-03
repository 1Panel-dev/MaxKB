import { ComplexPermission } from '@/utils/permission/type'

const applicationRouter = {
  path: '/application',
  name: 'application',
  meta: { title: 'views.application.title', permission: 'APPLICATION:READ' },
  redirect: '/application',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/application',
      name: 'application-index',
      meta: { title: '应用主页', activeMenu: '/application' },
      component: () => import('@/views/application/index.vue'),
      hidden: true,
    },
  ],
}

export default applicationRouter
