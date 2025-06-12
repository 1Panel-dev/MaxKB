import { Role, ComplexPermission } from '@/utils/permission/type'
const systemRouter = {
  path: '/system',
  name: 'system',
  meta: { title: 'views.system.title', permission: 'USER_MANAGEMENT:READ' },
  hidden: true,
  component: () => import('@/layout/layout-template/SystemMainLayout.vue'),
  children: [
    {
      path: '/system/user',
      name: 'user',
      meta: {
        icon: 'User',
        iconActive: 'UserFilled',
        title: 'views.userManage.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      component: () => import('@/views/user-manage/index.vue'),
    },
    {
      path: '/system/authorization',
      name: 'authorization',
      meta: {
        icon: 'app-resource-authorization',
        iconActive: 'app-resource-authorization-active',
        title: 'views.resourceAuthorization.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      component: () => import('@/views/resource-authorization/index.vue'),
    },
    {
      path: '/system/role',
      name: 'role',
      meta: {
        icon: 'app-resource-authorization', // TODO
        iconActive: 'app-resource-authorization-active', // TODO
        title: 'views.role.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      component: () => import('@/views/role/index.vue'),
    },
    {
      path: '/system/shared',
      name: 'shared',
      meta: {
        icon: 'app-folder-share',
        iconActive: 'app-folder-share-active',
        title: 'views.system.shared_resources',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      children: [
        {
          path: '/system/shared/knowledge',
          name: 'knowledgeBase',
          meta: {
            title: 'views.knowledge.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/knowledge-shared-system/index.vue'),
        },
        {
          path: '/system/shared/tool',
          name: 'tools',
          meta: {
            title: 'views.tool.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/tool-shared-system/index.vue'),
        },
        {
          path: '/system/shared/model',
          name: 'models',
          meta: {
            title: 'views.model.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/model-shared-system/index.vue'),
        },
      ],
    },
    {
      path: '/system/chat',
      name: 'SystemChat',
      meta: {
        icon: 'app-folder-share',
        iconActive: 'app-folder-share-active',
        title: '对话用户',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      children: [
        {
          path: '/system/chat/chat-user',
          name: 'ChatUser',
          meta: {
            title: '对话用户',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/system-chat-user/user-manage/index.vue'),
        },
        {
          path: '/system/chat/group',
          name: 'Group',
          meta: {
            title: '用户组',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/system-chat-user/group/index.vue'),
        },
        {
          path: '/system/chat/authentication',
          name: 'Authentication',
          meta: {
            title: '登录认证',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/system-chat-user/authentication/index.vue'),
        },
      ],
    },
    {
      path: '/system/setting',
      name: 'setting',
      meta: {
        icon: 'app-setting',
        iconActive: 'app-setting-active',
        title: 'views.system.subTitle',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      children: [
        {
          path: '/system/setting/theme',
          name: 'theme',
          meta: {
            title: 'views.system.theme.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            //permission: new ComplexPermission(['ADMIN'], ['x-pack'], 'AND')
          },
          component: () => import('@/views/theme/index.vue'),
        },
        {
          path: '/system/authentication',
          name: 'authentication',
          meta: {
            title: 'views.system.authentication.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            //permission: new ComplexPermission(['ADMIN'], ['x-pack'], 'AND')
          },
          component: () => import('@/views/authentication/index.vue'),
        },
        {
          path: '/system/email',
          name: 'email',
          meta: {
            title: 'views.system.email.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            //permission: new Role('ADMIN')
          },
          component: () => import('@/views/email/index.vue'),
        },
      ],
    },
  ],
}

export default systemRouter
