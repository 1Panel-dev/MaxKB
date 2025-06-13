import type { RouteRecordRaw } from 'vue-router'

export const routes: Array<RouteRecordRaw> = [
  // 对话
  {
    path: '/:accessToken',
    name: 'Chat',
    component: () => import('@/views/chat/index.vue'),
  },
  // 对话用户登录
  {
    path: '/user-login/:accessToken',
    name: 'UserLogin',
    component: () => import('@/views/chat/user-login/index.vue'),
  },
]
