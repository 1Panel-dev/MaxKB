import type { RouteRecordRaw } from 'vue-router'

/** System 来源的知识库详情路由，与 Workspace 复用页面组件。 */
export const systemKnowledgeRoutes: RouteRecordRaw[] = [
  {
    path: 'knowledge/:knowledgeId',
    name: 'system-knowledge-detail',
    component: () => import('@/views/knowledge/KnowledgeDetailView.vue'),
    meta: { title: '知识库详情', hidden: true },
  },
  {
    path: 'knowledge/:knowledgeId/document/:documentId',
    name: 'system-knowledge-document-detail',
    component: () => import('@/views/knowledge/DocumentDetailView.vue'),
    meta: { title: '文档详情', hidden: true },
  },
]
