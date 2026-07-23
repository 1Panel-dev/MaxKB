import type { RouteRecordRaw } from 'vue-router'

export const toolRoutes: RouteRecordRaw[] = [
  {
    path: 'tools',
    name: 'workspace-tools',
    component: () => import('@/views/home/HomeView.vue'),
    meta: { title: '工具', icon: 'icon_tools_outlined', order: 40 },
  },
]
