import type { RouteRecordRaw } from 'vue-router'

/** 登录及账户安全相关独立页面，不使用 AppLayout，也不会出现在左侧导航中。 */
export const loginRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { title: '登录' },
  },
]
