import type { RouteRecordRaw } from 'vue-router'
// const modules: any = import.meta.glob('./modules/*.ts', { eager: true })
// const rolesRoutes: RouteRecordRaw[] = [...Object.keys(modules).map((key) => modules[key].default)]

export const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },

  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue'),
  },
  {
    path: '/forget_password',
    name: 'ForgetPassword',
    component: () => import('@/views/login/ForgetPassword.vue')
  },
  {
    path: '/reset_password/:code/:email',
    name: 'ResetPassword',
    component: () => import('@/views/login/ResetPassword.vue')
  },
  // {
  //   path: '/:pathMatch(.*)',
  //   name: '404',
  //   component: () => import('@/views/404/index.vue')
  // }
]
