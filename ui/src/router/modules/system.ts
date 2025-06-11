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
    {
      path: '/system/role',
      name: 'role',
      meta: {
        icon: 'app-resource-authorization', // TODO
        iconActive: 'app-resource-authorization-active', // TODO
        title: 'views.role.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      component: () => import('@/views/role/index.vue'),
    },
    {
      path: '/system/setting',
      name: 'setting',
      meta: {
        icon: 'app-setting',
        iconActive: 'app-setting-active',
        title: 'views.system.subTitle',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      children: [
        {
          path: '/system/setting/theme',
          name: 'theme',
          meta: {
            title: 'views.system.theme.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            //permission: new ComplexPermission(['ADMIN'], ['x-pack'], 'AND')
          },
          component: () => import('@/views/theme/index.vue'),
        },
        {
          path: '/system/authentication',
          name: 'authentication',
          meta: {
            title: 'views.system.authentication.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            //permission: new ComplexPermission(['ADMIN'], ['x-pack'], 'AND')
          },
          component: () => import('@/views/authentication/index.vue'),
        },
        {
          path: '/system/email',
          name: 'email',
          meta: {
            title: 'views.system.email.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            //permission: new Role('ADMIN')
          },
          component: () => import('@/views/email/index.vue'),
        },
      ],
    },
  ],
}

export default systemRouter
