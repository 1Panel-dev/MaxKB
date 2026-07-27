import type { RouteRecordRaw } from 'vue-router'

export const homeRoutes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'workspace-home',
    component: () => import('@/views/home/HomeView.vue'),
    meta: {
      title: '首页',
      activeIcon: 'icon_home_filled',
      icon: 'icon_home_outlined',
      order: 10,
    },
  },
]
