import type { RouteRecordRaw } from 'vue-router'
import { Role } from '@/common/permission/type'
export const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/components/layout/home-layout/index.vue'),
    children: [
      {
        path: '/first',
        name: 'first',
        meta: { icon: 'app', title: '首页' },
        component: () => import('@/views/first/index.vue')
      },
      {
        path: '/app',
        name: 'app',
        meta: { icon: 'app', title: '应用', permission: 'APPLICATION:READ' },
        component: () => import('@/views/app/index.vue')
      },
      {
        path: '/dataset',
        name: 'dataset',
        meta: { icon: 'dataset', title: '数据集', permission: 'DATASET:READ' },
        component: () => import('@/views/dataset/index.vue')
      },
      {
        path: '/setting',
        name: 'setting',
        meta: { icon: 'setting', title: '系统设置', permission: 'SETTING:READ' },
        component: () => import('@/views/setting/index.vue')
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/login/register/index.vue')
  },
  {
    path: '/forgot_password',
    name: 'forgot_password',
    component: () => import('@/views/login/forgot-password/index.vue')
  },
  {
    path: '/reset_password/:code/:email',
    name: 'reset_password',
    component: () => import('@/views/login/reset-password/index.vue')
  },
  {
    path: '/:pathMatch(.*)',
    name: '404',
    component: () => import('@/views/404/index.vue')
  }
]
