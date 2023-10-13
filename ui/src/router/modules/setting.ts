const settingRouter = {
  path: '/setting',
  name: 'setting',
  meta: { icon: 'Setting', title: '系统设置', permission: 'SETTING:READ' },
  component: () => import('@/views/setting/index.vue')
}

export default settingRouter
