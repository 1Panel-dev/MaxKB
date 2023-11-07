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
        title: '团队管理',
        parentPath: '/setting',
        parentName: 'setting'
      },
      component: () => import('@/views/setting/index.vue')
    }
  ]
}

export default settingRouter
