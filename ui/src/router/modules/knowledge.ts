import { get_next_route } from '@/utils/permission'
import { PermissionConst, EditionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
const ModelRouter = {
  path: '/knowledge',
  name: 'knowledge',
  meta: {
    title: 'views.knowledge.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.KNOWLEDGE_READ.getWorkspacePermission,
      PermissionConst.KNOWLEDGE_READ.getWorkspacePermissionWorkspaceManageRole,
    ],
    icon: 'app-knowledge',
    iconActive: 'app-knowledge-active',
    group: 'workspace',
    order: 3,
  },
  redirect: '/knowledge',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/knowledge',
      name: 'knowledge-index',
      meta: { title: '知识库主页', activeMenu: '/knowledge', sameRoute: 'knowledge' },
      component: () => import('@/views/knowledge/index.vue'),
    },

    // 上传文档
    {
      path: '/knowledge/document/upload/:folderId/:type',
      name: 'UploadDocument',
      meta: {
        activeMenu: '/knowledge',
        permission: [
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return new ComplexPermission(
                [RoleConst.USER],
                [
                  PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(
                    to ? to.query.id : '',
                  ),
                ],
                [],
                'AND',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared' || to.params.folderId == 'resource-management') {
              return RoleConst.EXTENDS_ADMIN
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_CREATE
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getKnowledgeWorkspaceResourcePermission(
                to ? to.query.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return new ComplexPermission(
                [RoleConst.EXTENDS_USER.getWorkspaceRole()],
                [PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermission()],
                [],
                'AND',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return RoleConst.USER.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'resource-management') {
              return RoleConst.ADMIN
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'resource-management') {
              return PermissionConst.RESOURCE_KNOWLEDGE_DOCUMENT_CREATE
            }
          },
        ],
      },
      component: () => import('@/views/document/UploadDocument.vue'),
      hidden: true,
    },
    // 上传文档 - 飞书文档
    {
      path: '/knowledge/import/lark/:folderId',
      name: 'ImportLarkDocument',
      meta: {
        activeMenu: '/knowledge',
        permission: [
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return new ComplexPermission(
                [RoleConst.USER],
                [
                  PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(
                    to ? to.query.id : '',
                  ),
                ],
                [],
                'AND',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_CREATE
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getKnowledgeWorkspaceResourcePermission(
                to ? to.query.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_CREATE
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'resource-management') {
              return PermissionConst.RESOURCE_KNOWLEDGE_DOCUMENT_CREATE
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared' || to.params.folderId == 'resource-management') {
              return RoleConst.ADMIN
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared' || to.params.folderId == 'resource-management') {
              return RoleConst.EXTENDS_ADMIN
            }
          },
        ],
      },
      component: () => import('@/views/document/ImportLarkDocument.vue'),
      hidden: true,
    },
    // 上传文档 - 工作流
    {
      path: '/knowledge/import/workflow/:folderId',
      name: 'ImportWorkflowDocument',
      meta: {
        activeMenu: '/knowledge',
        permission: [
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return new ComplexPermission(
                [RoleConst.USER],
                [
                  PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(
                    to ? to.query.id : '',
                  ),
                ],
                [],
                'AND',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_CREATE
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getKnowledgeWorkspaceResourcePermission(
                to ? to.query.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_CREATE
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'resource-management') {
              return PermissionConst.RESOURCE_KNOWLEDGE_DOCUMENT_CREATE
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared' || to.params.folderId == 'resource-management') {
              return RoleConst.ADMIN
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared' || to.params.folderId == 'resource-management') {
              return RoleConst.EXTENDS_ADMIN
            }
          },
        ],
      },
      component: () => import('@/views/document/ImportWorkflowDocument.vue'),
      hidden: true,
    },
  ],
}

export default ModelRouter
