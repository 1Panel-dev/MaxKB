import type { RouteRecordRaw } from 'vue-router'
import perm from '@/permission'

export const homeRoutes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'workspace-home',
    component: () => import('@/views/home/index.vue'),
    meta: {
      title: 'overview.title',
      activeIcon: 'icon_screen_filled',
      icon: 'icon_screen_outlined',
      order: 10,
      permission: () => perm.homepage.homepage.read(),
      next: 'workspace-application',
    },
  },
]
