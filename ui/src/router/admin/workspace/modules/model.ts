import type { RouteRecordRaw } from 'vue-router'
import { perm } from '@/permission'

export const modelRoutes: RouteRecordRaw[] = [
  {
    path: 'model',
    name: 'workspace-model',
    component: () => import('@/views/model/index.vue'),
    meta: {
      title: 'model.title',
      icon: 'icon_dataset_outlined',
      activeIcon: 'icon_dataset_filled',
      order: 50,
      permission: () => perm.model.workspace.isShare(),
      next: 'workspace-trigger',
    },
  },
]
