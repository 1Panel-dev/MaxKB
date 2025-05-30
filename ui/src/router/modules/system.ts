import { Role, ComplexPermission } from '@/utils/permission/type'
const systemRouter = {
  path: '/system',
  name: 'system',
  meta: { title: 'views.system.title', permission: 'USER_MANAGEMENT:READ' },
  hidden: true,
  component: () => import('@/layout/layout-template/SystemMainLayout.vue'),
  children: [
    {
      path: '/system/user',
      name: 'user',
      meta: {
        icon: 'User',
        iconActive: 'UserFilled',
        title: 'views.userManage.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      component: () => import('@/views/user-manage/index.vue'),
    },
    {
      path: '/system/authorization',
      name: 'authorization',
      meta: {
        icon: 'app-resource-authorization',
        iconActive: 'app-resource-authorization-active',
        title: 'views.resourceAuthorization.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      component: () => import('@/views/resource-authorization/index.vue'),
    },
  ],
}

export default systemRouter
