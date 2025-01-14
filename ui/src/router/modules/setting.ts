import { hasPermission } from '@/utils/permission/index'
import Layout from '@/layout/layout-template/SystemLayout.vue'
import { Role, ComplexPermission } from '@/utils/permission/type'
import { t } from '@/locales'
const settingRouter = {
  path: '/setting',
  name: 'setting',
  meta: { icon: 'Setting', title: '系统设置', permission: 'SETTING:READ' },
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
        title: t('views.user.title'),
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
        title: t('views.team.title'),
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
        title: t('views.template.title'),
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
        title: t('views.system.title'),
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
            title: t('views.system.theme.title'),
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
            title: t('views.system.authentication.title'),
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
            title: t('views.system.email.title'),
            activeMenu: '/setting',
            parentPath: '/setting',
            parentName: 'setting',
            permission: new Role('ADMIN')
          },
          component: () => import('@/views/email/index.vue')
        }
      ]
    }
  ]
}

export default settingRouter
