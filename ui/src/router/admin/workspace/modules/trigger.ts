import type { RouteRecordRaw } from 'vue-router'

export const triggerRoutes: RouteRecordRaw[] = [
  {
    path: 'trigger',
    name: 'workspace-trigger',
    component: () => import('@/views/home/HomeView.vue'),
    meta: { title: '触发器', icon: 'icon_grid_outlined', order: 60 },
  },
]
