import type { RouteRecordRaw } from 'vue-router'

export const triggerRoutes: RouteRecordRaw[] = [
  {
    path: 'trigger',
    name: 'workspace-trigger',
    component: () => import('@/views/trigger/index.vue'),
    meta: { title: '触发器', icon: 'icon-laser', activeIcon: 'icon_laser_filled', order: 60 },
  },
]
