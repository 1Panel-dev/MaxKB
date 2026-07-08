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
        sameRoute: 'user',
        permission: [RoleConst.ADMIN, PermissionConst.USER_READ],
      },
      component: () => import('@/views/system/user-manage/index.vue'),
    },
    {
      path: '/system/workspace',
      name: 'workspace',
      meta: {
        icon: 'app-workspace',
        iconActive: 'app-workspace-active',
        title: 'views.workspace.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        sameRoute: 'workspace',
        permission: [
          new ComplexPermission(
            [RoleConst.WORKSPACE_MANAGE, RoleConst.ADMIN],
            [PermissionConst.WORKSPACE_WORKSPACE_READ, PermissionConst.WORKSPACE_READ],
            [EditionConst.IS_EE],
            'OR',
          ),
        ],
      },
      component: () => import('@/views/system/workspace/index.vue'),
    },
    {
      path: '/system/role',
      name: 'role',
      meta: {
        icon: 'app-role',
        iconActive: 'app-role-active',
        title: 'views.role.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        sameRoute: 'role',
        permission: [
          new ComplexPermission(
            [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE.getWorkspaceRole],
            [PermissionConst.ROLE_READ, PermissionConst.WORKSPACE_ROLE_READ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
        ],
      },
      component: () => import('@/views/system/role/index.vue'),
    },

    {
      path: '/system/resource-management',
      name: 'resourceManagement',
      meta: {
        icon: 'app-resource-management',
        iconActive: 'app-resource-management',
        title: 'views.system.resource_management.label',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        permission: [
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.RESOURCE_APPLICATION_READ],
            [EditionConst.IS_EE],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.RESOURCE_KNOWLEDGE_READ],
            [EditionConst.IS_EE],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.RESOURCE_TOOL_READ],
            [EditionConst.IS_EE],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.RESOURCE_MODEL_READ],
            [EditionConst.IS_EE],
            'OR',
          ),
        ],
      },
      children: [
        {
          path: '/system/resource-management/application',
          name: 'ApplicationResourceIndex',
          meta: {
            title: 'views.application.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            sameRoute: 'workspace',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.RESOURCE_APPLICATION_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
            ],
          },
          component: () =>
            import('@/views/system-resource-management/ApplicationResourceIndex.vue'),
        },
        {
          path: '/system/resource-management/knowledge',
          name: 'KnowledgeResourceIndex',
          meta: {
            title: 'views.knowledge.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            sameRoute: 'workspace',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.RESOURCE_KNOWLEDGE_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-resource-management/KnowledgeResourceIndex.vue'),
        },
        {
          path: '/system/resource-management/tool',
          name: 'ToolResourceIndex',
          meta: {
            title: 'views.tool.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            sameRoute: 'workspace',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.RESOURCE_TOOL_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-resource-management/ToolResourceIndex.vue'),
        },
        {
          path: '/system/resource-management/model',
          name: 'ModelResourceIndex',
          meta: {
            title: 'views.model.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.RESOURCE_MODEL_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-resource-management/ModelResourceIndex.vue'),
        },
      ],
    },
    {
      path: '/system/authorization',
      name: 'authorization',
      meta: {
        icon: 'app-resource-authorization',
        iconActive: 'app-resource-authorization-active',
        title: 'views.system.resourceAuthorization.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        sameRoute: 'authorization',
        permission: [
          new ComplexPermission(
            [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
            [
              PermissionConst.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
              PermissionConst.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                .getWorkspacePermissionWorkspaceManageRole,
            ],
            [],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
            [
              PermissionConst.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
              PermissionConst.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                .getWorkspacePermissionWorkspaceManageRole,
            ],
            [],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
            [
              PermissionConst.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
              PermissionConst.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                .getWorkspacePermissionWorkspaceManageRole,
            ],
            [],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
            [
              PermissionConst.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
              PermissionConst.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                .getWorkspacePermissionWorkspaceManageRole,
            ],
            [],
            'OR',
          ),
        ],
      },

      children: [
        {
          path: '/system/authorization/application',
          name: 'authorizationApplication',
          meta: {
            title: 'views.application.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            resource: 'APPLICATION',
            sameRoute: 'authorization',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                [
                  PermissionConst.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
                  PermissionConst.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                    .getWorkspacePermissionWorkspaceManageRole,
                ],
                [],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system/resource-authorization/index.vue'),
        },
        {
          path: '/system/authorization/knowledge',
          name: 'authorizationKnowledge',
          meta: {
            title: 'views.knowledge.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            resource: 'KNOWLEDGE',
            sameRoute: 'authorization',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                [
                  PermissionConst.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
                  PermissionConst.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                    .getWorkspacePermissionWorkspaceManageRole,
                ],
                [],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system/resource-authorization/index.vue'),
        },
        {
          path: '/system/authorization/tool',
          name: 'authorizationTool',
          meta: {
            title: 'views.tool.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            resource: 'TOOL',
            sameRoute: 'authorization',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                [
                  PermissionConst.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
                  PermissionConst.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                    .getWorkspacePermissionWorkspaceManageRole,
                ],
                [],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system/resource-authorization/index.vue'),
        },
        {
          path: '/system/authorization/model',
          name: 'authorizationModel',
          meta: {
            title: 'views.model.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            resource: 'MODEL',
            sameRoute: 'authorization',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN, RoleConst.WORKSPACE_MANAGE],
                [
                  PermissionConst.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_READ,
                  PermissionConst.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_READ
                    .getWorkspacePermissionWorkspaceManageRole,
                ],
                [],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system/resource-authorization/index.vue'),
        },
      ],
    },
    {
      path: '/system/shared',
      name: 'shared',
      meta: {
        icon: 'app-shared',
        iconActive: 'app-shared-active',
        title: 'views.shared.shared_resources',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        permission: [
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.SHARED_KNOWLEDGE_READ],
            [EditionConst.IS_EE],
            'OR',
          ),
          new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.SHARED_TOOL_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
          new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.SHARED_MODEL_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
        ],
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
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.SHARED_KNOWLEDGE_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-shared/KnowLedgeSharedIndex.vue'),
        },
        {
          path: '/system/shared/tool',
          name: 'tools',
          meta: {
            title: 'views.tool.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.SHARED_TOOL_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-shared/ToolSharedIndex.vue'),
        },
        {
          path: '/system/shared/model',
          name: 'models',
          meta: {
            title: 'views.model.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.SHARED_MODEL_READ],
                [EditionConst.IS_EE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-shared/ModelSharedIndex.vue'),
        },
      ],
    },
    {
      path: '/system/chat',
      name: 'SystemChat',
      meta: {
        icon: 'app-user-chat',
        iconActive: 'app-user-chat',
        title: 'views.chatUser.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        permission: [
          new ComplexPermission(
            [RoleConst.WORKSPACE_MANAGE, RoleConst.ADMIN],
            [PermissionConst.WORKSPACE_CHAT_USER_READ, PermissionConst.CHAT_USER_READ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.WORKSPACE_MANAGE, RoleConst.ADMIN],
            [PermissionConst.WORKSPACE_USER_GROUP_READ, PermissionConst.USER_GROUP_READ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.WORKSPACE_MANAGE, RoleConst.ADMIN],
            [PermissionConst.CHAT_USER_AUTH_READ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
        ],
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
            sameRoute: 'SystemChat',
            permission: [
              new ComplexPermission(
                [RoleConst.WORKSPACE_MANAGE, RoleConst.ADMIN],
                [PermissionConst.CHAT_USER_READ, PermissionConst.WORKSPACE_CHAT_USER_READ],
                [EditionConst.IS_EE, EditionConst.IS_PE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-chat-user/chat-user/index.vue'),
        },
        {
          path: '/system/chat/group',
          name: 'Group',
          meta: {
            title: 'views.chatUser.group.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            sameRoute: 'SystemChat',
            permission: [
              new ComplexPermission(
                [RoleConst.WORKSPACE_MANAGE, RoleConst.ADMIN],
                [PermissionConst.WORKSPACE_USER_GROUP_READ, PermissionConst.USER_GROUP_READ],
                [EditionConst.IS_EE, EditionConst.IS_PE],
                'OR',
              ),
            ],
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
            sameRoute: 'SystemChat',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.CHAT_USER_AUTH_READ],
                [EditionConst.IS_EE, EditionConst.IS_PE],
                'OR',
              ),
            ],
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
        sameRoute: 'setting',
        permission: [
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.APPEARANCE_SETTINGS_READ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.LOGIN_AUTH_READ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
          new ComplexPermission([RoleConst.ADMIN], [PermissionConst.EMAIL_SETTING_READ], [], 'OR'),
        ],
      },
      children: [
        {
          path: '/system/setting/theme',
          name: 'theme',
          meta: {
            title: 'theme.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            sameRoute: 'setting',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.APPEARANCE_SETTINGS_READ],
                [EditionConst.IS_EE, EditionConst.IS_PE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-setting/theme/index.vue'),
        },
        {
          path: '/system/authentication',
          name: 'SystemAuthentication',
          meta: {
            title: 'views.system.authentication.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            sameRoute: 'setting',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.LOGIN_AUTH_READ],
                [EditionConst.IS_EE, EditionConst.IS_PE],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-setting/authentication/index.vue'),
        },
        {
          path: '/system/email',
          name: 'email',
          meta: {
            title: 'views.system.email.title',
            activeMenu: '/system',
            parentPath: '/system',
            parentName: 'system',
            sameRoute: 'setting',
            permission: [
              new ComplexPermission(
                [RoleConst.ADMIN],
                [PermissionConst.EMAIL_SETTING_READ],
                [],
                'OR',
              ),
            ],
          },
          component: () => import('@/views/system-setting/email/index.vue'),
        },
      ],
    },
    {
      path: '/operate',
      name: 'operate',
      meta: {
        icon: 'app-document',
        iconActive: 'app-document-active',
        title: 'views.operateLog.title',
        activeMenu: '/system',
        parentPath: '/system',
        parentName: 'system',
        sameRoute: 'operate',
        permission: [
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.OPERATION_LOG_READ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
        ],
      },
      component: () => import('@/views/system/operate-log/index.vue'),
    },
  ],
}

export default systemRouter
