import type { RouteRecordRaw } from 'vue-router'

const modules: any = import.meta.glob('./modules/*.ts', { eager: true })

const rolesRoutes: RouteRecordRaw[] = [...Object.keys(modules).map((key) => modules[key].default)]

export const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    redirect: '/application',
    children: [
      ...rolesRoutes,
      {
        path: '/no-permission',
        name: 'noPermission',
        redirect: '/no-permission',
        meta: {},
        children: [
          {
            path: '/no-permission',
            name: 'noPermissionD',
            meta: {},
            component: () => import('@/views/error/NoPermission.vue'),
          },
        ],
        component: () => import('@/layout/layout-template/SimpleLayout.vue'),
      },
    ],
  },

  // 高级编排
  {
    path: '/application/:from/:id/workflow',
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
  {
    path: '/demo',
    name: 'demo',
    component: () => import('@/views/demo/index.vue'),
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
  {
    path: '/permission',
    name: 'permission',
    component: () => import('@/views/Permission.vue'),
  },
  {
    path: '/no-service',
    name: 'NoService',
    component: () => import('@/views/error/NoService.vue'),
  },
  {
    path: '/:pathMatch(.*)',
    name: '404',
    component: () => import('@/views/error/404.vue'),
  },
]
