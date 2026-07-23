import type { RouteRecordRaw } from 'vue-router'

export const knowledgeRoutes: RouteRecordRaw[] = [
  {
    path: 'knowledge',
    name: 'workspace-knowledge',
    redirect: { name: 'workspace-knowledge-list' },
    meta: { title: '知识库', icon: 'icon_reading_outlined', order: 30 },
    children: [
      {
        path: '',
        name: 'workspace-knowledge-list',
        component: () => import('@/views/home/HomeView.vue'),
        meta: { title: '知识库列表', hidden: true },
      },
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
