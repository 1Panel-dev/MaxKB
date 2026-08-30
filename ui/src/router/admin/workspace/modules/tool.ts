import type { RouteRecordRaw } from 'vue-router'

export const toolRoutes: RouteRecordRaw[] = [
  {
    path: 'tools',
    name: 'workspace-tools',
    component: () => import('@/views/tool/ToolView.vue'),
    meta: { title: '工具', icon: 'icon_busy_outlined', activeIcon: 'icon_busy__filled', order: 40 },
  },
]
