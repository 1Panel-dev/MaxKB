import Layout from '@/layout/main-layout/index.vue'
const applicationRouter = {
  path: '/application',
  name: 'application',
  meta: { title: '应用', permission: 'APPLICATION:READ' },
  redirect: '/application',
  children: [
    {
      path: '/application',
      name: 'application',
      component: () => import('@/views/application/index.vue')
    },
    {
      path: '/application/create',
      name: 'CreateApplication',
      meta: { activeMenu: '/application' },
      component: () => import('@/views/application/CreateAndSetting.vue'),
      hidden: true
    },
    {
      path: '/application/:id',
      name: 'ApplicationDetail',
      meta: { title: '应用详情', activeMenu: '/application' },
      component: Layout,
      hidden: true,
      children: [
        {
          path: 'overview',
          name: 'AppOverview',
          meta: {
            icon: 'app-all-menu',
            iconActive: 'app-all-menu-active',
            title: '概览',
            active: 'overview',
            parentPath: '/application/:id',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/application/AppOverview.vue')
        },
        {
          path: 'setting', 
          name: 'AppSetting',
          meta: {
            icon: 'Setting',
            title: '设置',
            active: 'setting',
            parentPath: '/application/:id',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/application/CreateAndSetting.vue')
        },
        {
          path: 'dialog',
          name: 'DialogLog',
          meta: {
            icon: 'Setting',
            title: '对话日志',
            active: 'dialog',
            parentPath: '/application/:id',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/application/DialogLog.vue')
        }
      ]
    },
  ]
}

export default applicationRouter
