import type { RouteRecordRaw } from 'vue-router'

export const homeRoutes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'workspace-home',
    component: () => import('@/views/home/HomeView.vue'),
    meta: { title: '首页', icon: 'icon_home_filled', order: 10 },
  },
]
