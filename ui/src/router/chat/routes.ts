import type { RouteRecordRaw } from 'vue-router'

export const routes: Array<RouteRecordRaw> = [
  // 对话
  {
    path: '/:accessToken',
    name: 'chat',
    component: () => import('@/views/chat/index.vue'),
  },
  // 对话用户登录
  {
    path: '/login/:accessToken',
    name: 'login',
    component: () => import('@/views/chat/user-login/index.vue'),
  },
  // 对话用户登录
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/404/index.vue'),
  },
]
