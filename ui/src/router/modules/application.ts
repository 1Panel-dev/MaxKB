import Layout from '@/layout/main-layout/index.vue'
const applicationRouter = {
  path: '/application',
  name: 'application',
  meta: { icon: 'app-applicaiton', title: '应用', permission: 'APPLICATION:READ' },
  redirect: '/application',
  children: [
    {
      path: '/application',
      name: 'application',
      component: () => import('@/views/application/index.vue')
    },
    {
      path: '/application/create', // create 
      name: 'CreateApplication',
      meta: { activeMenu: '/application' },
      component: () => import('@/views/application/CreateApplication.vue'),
      hidden: true
    },
    {
      path: '/application/:appId',
      name: 'ApplicationDetail',
      meta: { title: '应用详情', activeMenu: '/application' },
      component: Layout,
      hidden: true,
      children: [
        {
          path: 'overview',
          name: 'AppOverview',
          meta: {
            icon: 'Document',
            title: '概览',
            active: 'overview',
            parentPath: '/application/:appId',
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
            parentPath: '/application/:appId',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/application/AppSetting.vue')
        },
        {
          path: 'dialog',
          name: 'DialogLog',
          meta: {
            icon: 'Setting',
            title: '对话日志',
            active: 'dialog',
            parentPath: '/application/:appId',
            parentName: 'ApplicationDetail'
          },
          component: () => import('@/views/application/DialogLog.vue')
        }
      ]
    },
  ]
}

export default applicationRouter
