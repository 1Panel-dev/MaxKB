import type { RouteRecordRaw } from 'vue-router'

export const modelRoutes: RouteRecordRaw[] = [
  {
    path: 'model',
    name: 'workspace-model',
    component: () => import('@/views/home/HomeView.vue'),
    meta: { title: '模型', icon: 'icon_box_outlined', order: 50 },
  },
]
