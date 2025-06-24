import type { RouteRecordRaw } from 'vue-router'
const modules: any = import.meta.glob('./modules/*.ts', { eager: true })
import { hasPermission, set_next_route } from '@/utils/permission/index'
const rolesRoutes: RouteRecordRaw[] = [...Object.keys(modules).map((key) => modules[key].default)]
const get_workspace_permission_route = () => {
  const route = rolesRoutes.find((route: any) => {
    return (
      route.meta?.menu &&
      (route.meta.permission ? hasPermission(route.meta.permission as any, 'OR') : true)
    )
  })
  if (route?.name) {
    return { name: route?.name }
  }
  return { name: 'noPermission' }
}

export const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    redirect: '/application',
    children: [
      ...rolesRoutes.map((r) => {
        if (r.meta) {
          r.meta.get_permission_route = get_workspace_permission_route
        }
        return r
      }),
      {
        path: '/no-permission',
        name: 'noPermission',
        redirect: '/no-permission',
        meta: {},
        children: [
          {
            path: '/no-permission',
            name: 'noPermissionD',
            component: () => import('@/views/no-permission/index.vue'),
          },
        ],
        component: () => import('@/layout/layout-template/SimpleLayout.vue'),
      },
    ],
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
  {
    path: '/permission',
    name: 'permission',
    component: () => import('@/views/Permission.vue'),
  },
  // {
  //   path: '/:pathMatch(.*)',
  //   name: '404',
  //   component: () => import('@/views/404/index.vue')
  // }
]
