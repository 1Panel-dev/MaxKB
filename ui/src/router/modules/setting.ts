import Layout from '@/layout/main-layout/index.vue'
const settingRouter = {
  path: '/setting',
  name: 'setting',
  meta: { icon: 'Setting', title: '系统设置', permission: 'SETTING:READ' },
  redirect: '/setting',
  component: Layout,
  children: [
    {
      path: '/setting',
      name: 'setting',
      meta: {
        icon: 'app-team',
        iconActive: 'app-team-active',
        title: '团队管理',
        parentPath: '/setting',
        parentName: 'setting'
      },
      component: () => import('@/views/setting/index.vue')
    },
    {
      path: '/template',
      name: 'template',
      meta: {
        icon: 'app-template',
        iconActive: 'app-template-active',
        title: '模版管理',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'setting'
      },
      component: () => import('@/views/template/index.vue')
    }
  ]
}

export default settingRouter
