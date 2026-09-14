import type { RouteRecordRaw } from 'vue-router'

export const knowledgeRoutes: RouteRecordRaw[] = [
  {
    path: 'knowledge',
    name: 'workspace-knowledge',
    redirect: { name: 'workspace-knowledge-list' },
    meta: { title: '知识库', activeMenu: 'workspace-knowledge', icon: 'icon_book_outlined', activeIcon: 'icon_book_filled', order: 30 },
    children: [
      {
        path: '',
        name: 'workspace-knowledge-list',
        component: () => import('@/views/knowledge/KnowledgeView.vue'),
        meta: { title: '知识库列表', hidden: true },
      },
      {
        path: ':knowledgeId',
        name: 'workspace-knowledge-detail',
        component: () => import('@/views/knowledge-detail/WorkspaceKnowledgeDetailView.vue'),
        redirect: { name: 'workspace-knowledge-document-list' },
        meta: { title: '知识库详情', hidden: true },
        children: [
          {
            path: 'document',
            name: 'workspace-knowledge-document-list',
            component: () => import('@/views/knowledge-detail/document/DocumentListView.vue'),
            meta: { title: '文档', icon: 'icon-draft_outlined', activeIcon: 'icon-draft_outlined', order: 10 },
          },

          {
            path: 'workflow-entry',
            name: 'workspace-knowledge-workflow',
            redirect: (to) => ({ name: 'workflow-knowledge', params: { workspaceId: to.params.workspaceId, knowledgeId: to.params.knowledgeId } }),
            meta: { title: '工作流', icon: 'icon_ticket-flow_outlined', activeIcon: 'icon_ticket-flow_outlined', order: 20 },
          },
          {
            path: 'setting',
            name: 'workspace-knowledge-setting',
            component: () => import('@/views/knowledge-detail/setting/KnowledgeSettingView.vue'),
            meta: { title: '设置', icon: 'icon_setting', activeIcon: 'icon_setting_filled', order: 30 },
          },
          // {
          //   path: 'document/:documentId',
          //   name: 'workspace-knowledge-document-detail',
          //   component: () => import('@/views/knowledge-detail/DocumentDetailView.vue'),
          //   meta: { title: '文档详情', hidden: true, detailActiveMenu: 'workspace-knowledge-document-list' },
          // },
        ],
      },
    ],
  },
]
