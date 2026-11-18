import type { RouteRecordRaw } from 'vue-router'
import { perm } from '@/permission'

export const triggerRoutes: RouteRecordRaw[] = [
  {
    path: 'trigger',
    name: 'workspace-trigger',
    component: () => import('@/views/trigger/index.vue'),
    meta: {
      title: 'trigger.title',
      icon: 'icon-laser',
      activeIcon: 'icon_laser_filled',
      order: 60,
      permission: () => perm.trigger.read(),
      next: 'workspace-application',
    },
  },
]
