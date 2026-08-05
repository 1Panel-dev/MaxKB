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
        icon: 'icon-setting',
        order: 10,
      },
      children: [
        {
          path: 'users',
          name: 'system-users',
          component: () => import('@/views/system/identity/users/UserListView.vue'),
          meta: { title: '用户管理', order: 10 },
        },
        {
          path: 'workspace',
          name: 'system-workspace',
          component: () => import('@/views/system/identity/workspaces/WorkspaceListView.vue'),
          meta: { title: '工作空间', order: 20 },
        },
        {
          path: 'roles',
          name: 'system-roles',
          component: () => import('@/views/system/identity/roles/RoleListView.vue'),
          meta: { title: '角色管理', order: 30 },
        },
        {
          path: 'groups',
          name: 'system-groups',
          component: () => import('@/views/system/identity/groups/UserGroupListView.vue'),
          meta: { title: '用户组', order: 40 },
        },
        {
          path: 'authorization',
          name: 'system-authorization',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '资源授权', order: 50 },
        },
      ],
    },
    {
      path: 'resource',
      name: 'system-resource',
      redirect: { name: 'system-resource-applications' },
      meta: { title: '资源管理', icon: 'icon-setting', order: 20 },
      children: [
        {
          path: 'applications',
          name: 'system-resource-applications',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '智能体', order: 10 },
        },
        {
          path: 'knowledge',
          name: 'system-resource-knowledge',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '知识库', order: 20 },
        },
        {
          path: 'tools',
          name: 'system-resource-tools',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '工具', order: 30 },
        },
        {
          path: 'models',
          name: 'system-resource-models',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '模型', order: 40 },
        },
      ],
    },
    ...systemAgentRoutes,
    ...systemKnowledgeRoutes,
    {
      path: 'share',
      name: 'system-share',
      redirect: { name: 'system-shared-knowledge' },
      meta: { title: '共享资源', icon: 'icon-setting', order: 30 },
      children: [
        {
          path: 'knowledge',
          name: 'system-shared-knowledge',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '知识库', order: 10 },
        },
        {
          path: 'models',
          name: 'system-shared-models',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '模型', order: 20 },
        },
        {
          path: 'tools',
          name: 'system-shared-tools',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '工具', order: 30 },
        },
      ],
    },
    {
      path: 'chat',
      name: 'system-chat',
      redirect: { name: 'system-chat-users' },
      meta: { title: '对话端管理', icon: 'icon-setting', order: 40 },
      children: [
        {
          path: 'users',
          name: 'system-chat-users',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '对话用户', order: 10 },
        },
        {
          path: 'groups',
          name: 'system-chat-groups',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '对话用户组', order: 20 },
        },
        {
          path: 'authentication',
          name: 'system-chat-authentication',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '对话用户认证', order: 30 },
        },
        {
          path: 'portal-access',
          name: 'system-portal-access',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '门户访问设置', order: 40 },
        },
      ],
    },
    {
      path: 'settings',
      name: 'system-settings',
      redirect: { name: 'system-login-authentication' },
      meta: { title: '系统设置', icon: 'icon-setting', order: 50 },
      children: [
        {
          path: 'authentication',
          name: 'system-login-authentication',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '系统用户认证', order: 10 },
        },
        {
          path: 'appearance',
          name: 'system-appearance',
          component: () => import('@/views/system/settings/AppearanceSettingsView.vue'),
          meta: { title: '外观设置', order: 20 },
        },
        {
          path: 'email',
          name: 'system-email',
          component: () => import('@/views/system/SystemView.vue'),
          meta: { title: '邮箱设置', order: 30 },
        },
      ],
    },
    {
      path: 'logs',
      name: 'system-logs',
      component: () => import('@/views/system/SystemView.vue'),
      meta: { title: '操作日志', icon: 'icon-setting', order: 60 },
    },
  ],
}
