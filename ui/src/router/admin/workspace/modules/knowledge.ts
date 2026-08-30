import type { RouteRecordRaw } from 'vue-router'

export const knowledgeRoutes: RouteRecordRaw[] = [
  {
    path: 'knowledge',
    name: 'workspace-knowledge',
    redirect: { name: 'workspace-knowledge-list' },
    meta: { title: '知识库', activeMenu: 'workspace-knowledge', icon: 'icon_book_outlined', activeIcon: 'icon_book_filled', order: 30 },
    children: [
      { path: '', name: 'workspace-knowledge-list', component: () => import('@/views/knowledge/KnowledgeView.vue'), meta: { title: '知识库列表', hidden: true } },
      {
        path: ':knowledgeId',
        name: 'workspace-knowledge-detail',
        component: () => import('@/views/knowledge/KnowledgeDetailView.vue'),
        meta: { title: '知识库详情', hidden: true },
      },
      {
        path: ':knowledgeId/document/:documentId',
        name: 'workspace-knowledge-document-detail',
        component: () => import('@/views/knowledge/DocumentDetailView.vue'),
        meta: { title: '文档详情', hidden: true },
      },
    ],
  },
]
