import { hasPermission } from '@/utils/permission/index'
import Layout from '@/layout/layout-template/SystemLayout.vue'
import { Role, ComplexPermission } from '@/utils/permission/type'
const settingRouter = {
  path: '/setting',
  name: 'setting',
  meta: { icon: 'Setting', title: 'views.system.title', permission: 'SETTING:READ' },
  redirect: () => {
    if (hasPermission(new Role('ADMIN'), 'AND')) {
      return '/user'
    }
    return '/team'
  },
  component: Layout,
  children: [
    {
      path: '/user',
      name: 'user',
      meta: {
        icon: 'User',
        iconActive: 'UserFilled',
        title: 'views.user.title',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting',
        permission: new Role('ADMIN')
      },
      component: () => import('@/views/user-manage/index.vue')
    },
    {
      path: '/team',
      name: 'team',
      meta: {
        icon: 'app-team',
        iconActive: 'app-team-active',
        title: 'views.team.title',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting'
      },
      component: () => import('@/views/team/index.vue')
    },
    {
      path: '/template',
      name: 'template',
      meta: {
        icon: 'app-template',
        iconActive: 'app-template-active',
        title: 'views.template.title',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting'
      },
      component: () => import('@/views/template/index.vue')
    },
    {
      path: '/system',
      name: 'system',
      meta: {
        icon: 'app-setting',
        iconActive: 'app-setting-active',
        title: 'views.system.subTitle',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting',
        permission: new Role('ADMIN')
      },
      children: [
        {
          path: '/system/theme',
          name: 'theme',
          meta: {
            title: 'views.system.theme.title',
            activeMenu: '/setting',
            parentPath: '/setting',
            parentName: 'setting',
            permission: new ComplexPermission(['ADMIN'], ['x-pack'], 'AND')
          },
          component: () => import('@/views/theme/index.vue')
        },
        {
          path: '/system/authentication',
          name: 'authentication',
          meta: {
            title: 'views.system.authentication.title',
            activeMenu: '/setting',
            parentPath: '/setting',
            parentName: 'setting',
            permission: new ComplexPermission(['ADMIN'], ['x-pack'], 'AND')
          },
          component: () => import('@/views/authentication/index.vue')
        },
        {
          path: '/system/email',
          name: 'email',
          meta: {
            title: 'views.system.email.title',
            activeMenu: '/setting',
            parentPath: '/setting',
            parentName: 'setting',
            permission: new Role('ADMIN')
          },
          component: () => import('@/views/email/index.vue')
        }
      ]
    },
    {
      path: '/operate',
      name: 'operate',
      meta: {
        icon: 'app-document',
        iconActive: 'app-document-active',
        title: 'views.operateLog.title',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting',
        permission: new ComplexPermission(['ADMIN'], ['x-pack'], 'AND')
      },
      component: () => import('@/views/operate-log/index.vue')
    }
  ]
}

export default settingRouter
