import type { RouteRecordRaw } from 'vue-router'

export const homeRoutes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'workspace-home',
    component: () => import('@/views/home/index.vue'),
    meta: { title: '概览', activeIcon: 'icon_screen_filled', icon: 'icon_screen_outlined', order: 10 },
  },
]
