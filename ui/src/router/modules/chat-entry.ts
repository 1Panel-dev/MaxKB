import { PermissionConst, RoleConst } from '@/utils/permission/data'

/**
 * 顶级菜单「对话」——直接的对话入口。
 *
 * 设计目的：解决"必须先进入应用 → 找到目标 → 才能对话"的多步流程，
 * 把所有已发布的智能体集中到一个卡片网格里，点一下就开聊。
 *
 * 权限：与「应用」菜单相同，凡是能看到应用列表的用户都能进。
 */
const chatEntryRouter = {
  path: '/chat-entry',
  name: 'chat-entry',
  meta: {
    title: 'views.chatEntry.title',
    menu: true,
    permission: [
      RoleConst.USER.getWorkspaceRole,
      RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermissionWorkspaceManageRole,
      PermissionConst.APPLICATION_READ.getWorkspacePermission,
    ],
    icon: 'app-user-chat',
    iconActive: 'app-user-chat-active',
    group: 'workspace',
    // 放在最前面（application=1，知识库=2，工具=3，模型=4）
    order: 0,
  },
  redirect: '/chat-entry',
  component: () => import('@/layout/layout-template/SimpleLayout.vue'),
  children: [
    {
      path: '/chat-entry',
      name: 'chat-entry-index',
      meta: {
        title: 'views.chatEntry.title',
        activeMenu: '/chat-entry',
        sameRoute: 'chat-entry',
      },
      component: () => import('@/views/chat-entry/index.vue'),
      hidden: true,
    },
  ],
}

export default chatEntryRouter
