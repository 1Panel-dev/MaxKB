import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
const systemRouter = {
  path: '/system',
  name: 'system',
  meta: { title: 'views.system.title' },
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
        permission: [RoleConst.ADMIN,EditionConst.IS_EE],
      },
      component: () => import('@/views/user-manage/index.vue'),
    },
    {
      path: '/system/resource-management',
      name: 'resourceManagement',
      meta: {
        icon: 'app-folder-share',
        iconActive: 'app-folder-share-active',
        title: 'views.system.resource_management',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
      },
      children: [
        {
          path: '/system/resource-management/knowledge',
          name: 'knowledgeResourceManagement',
          meta: {
            title: 'views.knowledge.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/resource-management/knowledge/index.vue'),
        },
        {
          path: '/system/resource-management/tool',
          name: 'toolResourceManagement',
          meta: {
            title: 'views.tool.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
          },
          component: () => import('@/views/resource-management/tool/index.vue'),
        },
      ],
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
        permission:[new ComplexPermission([RoleConst.ADMIN,RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],[PermissionConst.ROLE_READ],[EditionConst.IS_EE],'OR'),],
      },
      component: () => import('@/views/role/index.vue'),
    },
    {
      path: '/system/workspace',
      name: 'workspace',
      meta: {
        icon: 'app-resource-authorization', // TODO
        iconActive: 'app-resource-authorization-active', // TODO
        title: 'views.workspace.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        permission:[new ComplexPermission([RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,RoleConst.ADMIN],[PermissionConst.WORKSPACE_WORKSPACE_READ],[EditionConst.IS_EE],'OR'),],
      },
      component: () => import('@/views/workspace/index.vue'),
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
        permission: [EditionConst.IS_EE],
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
          component: () => import('@/views/shared/knowledge-shared/index.vue'),
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
          component: () => import('@/views/shared/tool-shared/index.vue'),
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
          component: () => import('@/views/shared/model-shared/index.vue'),
        },
      ],
    },
    {
      path: '/system/chat',
      name: 'SystemChat',
      meta: {
        icon: 'app-folder-share',
        iconActive: 'app-folder-share-active',
        title: 'views.chatUser.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        permission:[new ComplexPermission([RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,RoleConst.ADMIN],[PermissionConst.WORKSPACE_USER_GROUP_READ],[EditionConst.IS_EE,EditionConst.IS_PE],'OR'),],
      },
      children: [
        {
          path: '/system/chat/chat-user',
          name: 'ChatUser',
          meta: {
            title: 'views.chatUser.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            permission:[new ComplexPermission([RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,RoleConst.ADMIN],[PermissionConst.WORKSPACE_CHAT_USER_READ],[EditionConst.IS_EE,EditionConst.IS_PE],'OR'),],
          },
          component: () => import('@/views/system-chat-user/user-manage/index.vue'),
        },
        {
          path: '/system/chat/group',
          name: 'Group',
          meta: {
            title: 'views.chatUser.group.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            permission:[new ComplexPermission([RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,RoleConst.ADMIN],[PermissionConst.WORKSPACE_USER_GROUP_READ],[EditionConst.IS_EE,EditionConst.IS_PE],'OR'),],
          },
          component: () => import('@/views/system-chat-user/group/index.vue'),
        },
        {
          path: '/system/chat/authentication',
          name: 'Authentication',
          meta: {
            title: 'views.system.authentication.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            permission:[new ComplexPermission([RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,RoleConst.ADMIN],
              [PermissionConst.CHAT_USER_AUTH_READ],[EditionConst.IS_EE,EditionConst.IS_PE],'OR'),],
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
            permission: [EditionConst.IS_PE, EditionConst.IS_EE],
          },
          component: () => import('@/views/theme/index.vue'),
        },
        {
          path: '/system/authentication',
          name: 'SystemAuthentication',
          meta: {
            title: 'views.system.authentication.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            permission: [EditionConst.IS_PE, EditionConst.IS_EE],
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
