import type { RouteRecordRaw } from 'vue-router'

export const modelRoutes: RouteRecordRaw[] = [
  {
    path: 'model',
    name: 'workspace-model',
    component: () => import('@/views/home/HomeView.vue'),
    meta: {
      title: '模型',
      icon: 'icon_dataset_outlined',
      activeIcon: 'icon_dataset_outlined',
      order: 50,
    },
  },
]
