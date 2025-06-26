import { SourceTypeEnum } from '@/enums/common'
import { get_next_route } from '@/utils/permission'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
const DocumentRouter = {
  path: '/knowledge/:id/:folderId',
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
        parentPath: '/knowledge/:id/:folderId',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
        permission: [
          RoleConst.ADMIN,
          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
          () => {
            const to: any = get_next_route()
            return PermissionConst.KNOWLEDGE_DOCUMENT_READ.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            )
          },
          PermissionConst.KNOWLEDGE_READ.getWorkspacePermissionWorkspaceManageRole,
        ],
      },
      component: () => import('@/views/document/index.vue'),
    },
    {
      path: 'problem',
      name: 'Problem',
      meta: {
        icon: 'app-problems',
        iconActive: 'QuestionFilled',
        title: 'views.problem.title',
        active: 'problem',
        parentPath: '/knowledge/:id/:folderId',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
        permission: [
          RoleConst.ADMIN,
          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
          () => {
            const to: any = get_next_route()
            return PermissionConst.KNOWLEDGE_PROBLEM_READ.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            )
          },
          PermissionConst.KNOWLEDGE_PROBLEM_READ.getWorkspacePermissionWorkspaceManageRole,
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
        parentPath: '/knowledge/:id/:folderId',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
      },
      component: () => import('@/views/hit-test/index.vue'),
    },
    {
      path: 'chat-user',
      name: 'KnowledgeChatUser',
      meta: {
        icon: 'app-document',
        iconActive: 'app-document-active',
        title: 'views.chatUser.title',
        active: 'chat-log',
        parentPath: '/knowledge/:id/:folderId',
        parentName: 'KnowledgeDetail',
        resourceType: SourceTypeEnum.KNOWLEDGE,
        group: 'KnowledgeDetail',
        permission: [
          RoleConst.ADMIN,
          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
          () => {
            const to: any = get_next_route()
            return PermissionConst.WORKSPACE_CHAT_USER_READ.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            )
          },
          PermissionConst.WORKSPACE_CHAT_USER_READ.getWorkspacePermissionWorkspaceManageRole,
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
        parentPath: '/knowledge/:id/:folderId',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
        permission: [
          RoleConst.ADMIN,
          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
          () => {
            const to: any = get_next_route()
            return PermissionConst.KNOWLEDGE_EDIT.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            )
          },
          PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermissionWorkspaceManageRole,
        ],
      },
      component: () => import('@/views/knowledge/KnowledgeSetting.vue'),
    },
  ],
}

export default DocumentRouter
