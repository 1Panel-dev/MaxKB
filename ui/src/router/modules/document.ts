import { SourceTypeEnum } from '@/enums/common'
import { get_next_route } from '@/utils/permission'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'
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
          () => {
            const to: any = get_next_route()
            if (to.params.folder_id == 'shared') {
               return RoleConst.ADMIN
            }else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole
            }
          },
          () => {
            const to: any = get_next_route()

            if (to.params.folderId == 'shared') {

              return PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_READ } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_READ.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            )}
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared'){ return RoleConst.ADMIN } else {
              return PermissionConst.KNOWLEDGE_DOCUMENT_READ.getWorkspacePermissionWorkspaceManageRole
            }
          }
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
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return RoleConst.ADMIN } else { return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return PermissionConst.SHARED_KNOWLEDGE_PROBLEM_READ } else { return PermissionConst.KNOWLEDGE_PROBLEM_READ.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            ) }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return RoleConst.ADMIN } else { return PermissionConst.KNOWLEDGE_PROBLEM_READ.getWorkspacePermissionWorkspaceManageRole }
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
        parentPath: '/knowledge/:id/:folderId',
        parentName: 'KnowledgeDetail',
        group: 'KnowledgeDetail',
        permission: [
          RoleConst.ADMIN,
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return RoleConst.ADMIN } else { return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return PermissionConst.SHARED_KNOWLEDGE_HIT_TEST_READ } else { return PermissionConst.KNOWLEDGE_HIT_TEST_READ.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            ) }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return RoleConst.ADMIN } else { return PermissionConst.KNOWLEDGE_HIT_TEST_READ.getWorkspacePermissionWorkspaceManageRole }
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
        iconActive: 'app-user-chat',
        title: 'views.chatUser.title',
        active: 'chat-log',
        parentPath: '/knowledge/:id/:folderId',
        parentName: 'KnowledgeDetail',
        resourceType: SourceTypeEnum.KNOWLEDGE,
        group: 'KnowledgeDetail',
        permission: new ComplexPermission([    RoleConst.ADMIN,
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return RoleConst.ADMIN
            } else {
              return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole()
            }
          },],[
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') {
              return PermissionConst.SHARED_KNOWLEDGE_CHAT_USER_READ
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
            } else { return PermissionConst.KNOWLEDGE_CHAT_USER_READ.getWorkspacePermissionWorkspaceManageRole() }
          },
        ],[EditionConst.IS_EE,EditionConst.IS_PE],'OR'),
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
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return RoleConst.ADMIN } else { return RoleConst.WORKSPACE_MANAGE.getWorkspaceRole }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return PermissionConst.SHARED_KNOWLEDGE_EDIT } else { return PermissionConst.KNOWLEDGE_EDIT.getKnowledgeWorkspaceResourcePermission(
              to ? to.params.id : '',
            ) }
          },
          () => {
            const to: any = get_next_route()
            if (to.params.folderId == 'shared') { return RoleConst.ADMIN } else { return PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermissionWorkspaceManageRole }
          },
        ],
      },
      component: () => import('@/views/knowledge/KnowledgeSetting.vue'),
    },
  ],
}

export default DocumentRouter
