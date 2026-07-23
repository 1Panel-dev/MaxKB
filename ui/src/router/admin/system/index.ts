import type { RouteRecordRaw } from 'vue-router'
import { systemAgentRoutes } from './modules/agent'
import { systemKnowledgeRoutes } from './modules/knowledge'

export const systemRoutes: RouteRecordRaw = {
  path: '/system',
  component: () => import('@/layout/AppLayout.vue'),
  redirect: { name: 'system-users' },
  meta: { scope: 'system' },
  children: [
    {
      path: 'identity',
      name: 'system-identity',
      redirect: { name: 'system-users' },
      meta: {
        title: '身份与权限',
        icon: 'icon_user_outlined',
        order: 10,
      },
      children: [
        {
          path: 'users',
          name: 'system-users',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '用户管理', order: 10 },
        },
        {
          path: 'roles',
          name: 'system-roles',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '角色管理', order: 20 },
        },
        {
          path: 'workspace',
          name: 'system-workspace',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '工作空间', order: 30 },
        },
        {
          path: 'groups',
          name: 'system-groups',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '用户组', order: 40 },
        },
      ],
    },
    {
      path: 'resource',
      name: 'system-resource',
      redirect: { name: 'system-resource-list' },
      meta: { title: '资源管理', icon: 'icon_folder_outlined', order: 20 },
      children: [
        {
          path: '',
          name: 'system-resource-list',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '资源列表', hidden: true },
        },
      ],
    },
    ...systemAgentRoutes,
    ...systemKnowledgeRoutes,
    {
      path: 'share',
      name: 'system-share',
      component: () => import('@/views/system/SystemView.vue'),
      meta: { title: '共享资源', icon: 'icon_folder_outlined', order: 30 },
    },
    {
      path: 'authorization',
      name: 'system-authorization',
      component: () => import('@/views/system/SystemView.vue'),
      meta: { title: '资源授权', icon: 'icon_lock_outlined', order: 40 },
    },
    {
      path: 'chat',
      name: 'system-chat',
      component: () => import('@/views/system/SystemView.vue'),
      meta: { title: '对话端管理', icon: 'icon_chat_outlined', order: 50 },
    },
    {
      path: 'settings',
      name: 'system-settings',
      component: () => import('@/views/system/SystemView.vue'),
      meta: { title: '系统设置', icon: 'icon_setting_outlined', order: 60 },
    },
    {
      path: 'logs',
      name: 'system-logs',
      component: () => import('@/views/system/SystemView.vue'),
      meta: { title: '操作日志', icon: 'icon_document_outlined', order: 70 },
    },
  ],
}
