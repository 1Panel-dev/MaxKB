import { SourceTypeEnum } from '@/enums/common'
import { get_next_route } from '@/utils/permission'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
/* type 类型
    BASE = 0, '通用类型'
    WEB = 1, 'web站点类型'
    LARK = 2, '飞书类型'
    YUQUE = 3, '语雀类型'
    WORKFLOW = 4, '工作流类型'
*/
const DocumentRouter = {
  path: '/knowledge/:id/:folderId/:type',
  name: 'KnowledgeDetail',
  meta: { title: 'common.fileUpload.document', activeMenu: '/knowledge', breadcrumb: true },
  component: () => import('@/layout/layout-template/MainLayout.vue'),
  hidden: true,
  children: [
    {
      path: 'document',
      name: 'Document',
      meta: {
        icon: 'app-document',
        iconActive: 'app-document-active',
        title: 'common.fileUpload.document',
        active: 'document',
        parentPath: '/knowledge/:id/:folderId/:type',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
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
                    to ? to.params.id : '',
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
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_READ
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_READ.getKnowledgeWorkspaceResourcePermission(
                to ? to.params.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_READ.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return new ComplexPermission(
                [RoleConst.EXTENDS_USER.getWorkspaceRole()],
                [PermissionConst.KNOWLEDGE_DOCUMENT_READ.getWorkspacePermission()],
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
              return PermissionConst.RESOURCE_KNOWLEDGE_DOCUMENT_READ
            }
          },
        ],
      },
      component: () => import('@/views/document/index.vue'),
    },
    {
      path: 'knowledge-workflow-setting',
      name: 'knowledgeWorkflowSetting',
      meta: {
        title: 'views.workflow.workflow',
        icon: 'app-problems',
        activeMenu: '/knowledge',
        parentPath: '/knowledge/:id/:folderId/:type',
        parentName: 'KnowledgeDetail',
        resourceType: SourceTypeEnum.KNOWLEDGE,
        group: 'KnowledgeDetail',
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
                    to ? to.params.id : '',
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
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_WORKFLOW_READ
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_WORKFLOW_READ.getKnowledgeWorkspaceResourcePermission(
                to ? to.params.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_WORKFLOW_READ.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return new ComplexPermission(
                [RoleConst.EXTENDS_USER.getWorkspaceRole()],
                [PermissionConst.KNOWLEDGE_WORKFLOW_READ.getWorkspacePermission()],
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
              return PermissionConst.RESOURCE_KNOWLEDGE_WORKFLOW_READ
            }
          },
        ].map((p) => () => {
          const to: any = get_next_route()
          if (to.params.type !== '4') {
            return false
          }
          return p()
        }),
      },
      redirect: (menu: any) => {
        return `/knowledge/${menu.params.id}/${menu.params.folderId}/workflow`
      },
      component: () => import('@/views/knowledge/index.vue'),
    },
    {
      path: 'problem',
      name: 'Problem',
      meta: {
        icon: 'app-problems',
        iconActive: 'QuestionFilled',
        title: 'views.problem.title',
        active: 'problem',
        parentPath: '/knowledge/:id/:folderId/:type',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
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
                    to ? to.params.id : '',
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
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_PROBLEM_READ
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_PROBLEM_READ.getKnowledgeWorkspaceResourcePermission(
                to ? to.params.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_PROBLEM_READ.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return new ComplexPermission(
                [RoleConst.EXTENDS_USER.getWorkspaceRole()],
                [PermissionConst.KNOWLEDGE_PROBLEM_READ.getWorkspacePermission()],
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
              return PermissionConst.RESOURCE_KNOWLEDGE_PROBLEM_READ
            }
          },
        ],
      },
      component: () => import('@/views/problem/index.vue'),
    },
    {
      path: 'hit-test',
      name: 'KnowledgeHitTest',
      meta: {
        icon: 'app-hit-test',
        title: 'views.application.hitTest.title',
        active: 'hit-test',
        parentPath: '/knowledge/:id/:folderId/:type',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
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
                    to ? to.params.id : '',
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
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_HIT_TEST_READ
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_HIT_TEST_READ.getKnowledgeWorkspaceResourcePermission(
                to ? to.params.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_HIT_TEST_READ.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return new ComplexPermission(
                [RoleConst.EXTENDS_USER.getWorkspaceRole()],
                [PermissionConst.KNOWLEDGE_HIT_TEST_READ.getWorkspacePermission()],
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
              return PermissionConst.RESOURCE_KNOWLEDGE_HIT_TEST
            }
          },
        ],
      },
      component: () => import('@/views/hit-test/index.vue'),
    },
    {
      path: 'chat-user',
      name: 'KnowledgeChatUser',
      meta: {
        icon: 'app-user-chat',
        iconActive: 'app-user-chat-active',
        title: 'views.chatUser.title',
        active: 'chat-user',
        parentPath: '/knowledge/:id/:folderId/:type',
        parentName: 'KnowledgeDetail',
        resourceType: SourceTypeEnum.KNOWLEDGE,
        group: 'KnowledgeDetail',
        permission: [
          new ComplexPermission(
            [
              RoleConst.ADMIN,
              () => {
                const to: any = get_next_route()
                if (to.params.folderId == 'shared') {
                  return RoleConst.ADMIN
                } else if (to.params.folderId == 'resource-management') {
                  return RoleConst.ADMIN
                } else {
                  return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
                }
              },
            ],
            [
              () => {
                const to: any = get_next_route()
                if (to.params.folderId == 'shared') {
                  return PermissionConst.SHARED_KNOWLEDGE_CHAT_USER_READ
                } else if (to.params.folderId == 'resource-management') {
                  return PermissionConst.RESOURCE_KNOWLEDGE_CHAT_USER_READ
                } else {
                  return PermissionConst.KNOWLEDGE_CHAT_USER_READ.getKnowledgeWorkspaceResourcePermission(
                    to ? to.params.id : '',
                  )
                }
              },
              () => {
                const to: any = get_next_route()
                if (to.params.folder_id == 'shared') {
                  return PermissionConst.SHARED_KNOWLEDGE_CHAT_USER_READ
                } else if (to.params.folderId == 'resource-management') {
                  return PermissionConst.RESOURCE_KNOWLEDGE_CHAT_USER_READ
                } else {
                  return PermissionConst.KNOWLEDGE_CHAT_USER_READ.getWorkspacePermissionWorkspaceManageRole()
                }
              },
            ],
            [EditionConst.IS_EE, EditionConst.IS_PE],
            'OR',
          ),
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
                    to ? to.params.id : '',
                  ),
                ],
                [EditionConst.IS_EE, EditionConst.IS_PE],
                'AND',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return new ComplexPermission(
                [RoleConst.EXTENDS_USER.getWorkspaceRole()],
                [PermissionConst.KNOWLEDGE_CHAT_USER_READ.getWorkspacePermission()],
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
              return PermissionConst.RESOURCE_KNOWLEDGE_CHAT_USER_READ
            }
          },
        ],
      },
      component: () => import('@/views/chat-user/index.vue'),
    },
    {
      path: 'setting',
      name: 'KnowledgeSetting',
      meta: {
        icon: 'app-setting',
        iconActive: 'app-setting-active',
        title: 'common.setting',
        active: 'setting',
        parentPath: '/knowledge/:id/:folderId/:type',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
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
                    to ? to.params.id : '',
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
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_EDIT
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_EDIT.getKnowledgeWorkspaceResourcePermission(
                to ? to.params.id : '',
              )
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else if (to.params.folderId == 'resource-management') {
            } else {
              return PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermissionWorkspaceManageRole()
            }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'share') {
              return new ComplexPermission(
                [RoleConst.EXTENDS_USER.getWorkspaceRole()],
                [PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermission()],
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
              return PermissionConst.RESOURCE_KNOWLEDGE_EDIT
            }
          },
        ],
      },
      component: () => import('@/views/knowledge/KnowledgeSetting.vue'),
    },
  ],
}

export default DocumentRouter
