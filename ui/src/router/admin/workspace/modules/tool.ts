import type { RouteRecordRaw } from 'vue-router'
import { perm } from '@/permission'

export const toolRoutes: RouteRecordRaw[] = [
  {
    path: 'tools',
    name: 'workspace-tools',
    component: () => import('@/views/tool/index.vue'),
    meta: { title: '工具',
      icon: 'icon_busy_outlined',
      activeIcon: 'icon_busy__filled', order: 40,
      permission: () => perm.tool.workspace.isShare(),
      next: 'workspace-model',
    },
  },
]
