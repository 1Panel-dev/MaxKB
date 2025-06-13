import type { RouteRecordRaw } from 'vue-router'
const modules: any = import.meta.glob('./modules/*.ts', { eager: true })
const rolesRoutes: RouteRecordRaw[] = [...Object.keys(modules).map((key) => modules[key].default)]

export const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    redirect: '/application',
    children: [...rolesRoutes],
  },

  // 高级编排
  {
    path: '/application/:id/workflow',
    name: 'ApplicationWorkflow',
    meta: { activeMenu: '/application' },
    component: () => import('@/views/application-workflow/index.vue'),
  },
  // 对话
  {
    path: '/chat/:accessToken',
    name: 'Chat',
    component: () => import('@/views/chat/index.vue'),
  },

  // 对话用户登录
  {
    path: '/user-login/:accessToken',
    name: 'UserLogin',
    component: () => import('@/views/chat/user-login/index.vue'),
  },

  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue'),
  },
  {
    path: '/forgot_password',
    name: 'ForgotPassword',
    component: () => import('@/views/login/ForgotPassword.vue'),
  },
  {
    path: '/reset_password/:code/:email',
    name: 'ResetPassword',
    component: () => import('@/views/login/ResetPassword.vue'),
  },
  // {
  //   path: '/:pathMatch(.*)',
  //   name: '404',
  //   component: () => import('@/views/404/index.vue')
  // }
]
