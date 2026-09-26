import type { RouteRecordRaw } from 'vue-router'

/** 工作空间知识库模块下的共享详情路由。 */
export const sharedKnowledgeRoutes: RouteRecordRaw[] = [
  {
    path: 'shared/knowledge/:knowledgeId/:type',
    name: 'workspace-shared-knowledge-detail',
    component: () => import('@/views/knowledge-detail/index.vue'),
    redirect: { name: 'workspace-shared-knowledge-document-list' },
    meta: { title: '共享知识库详情', hidden: true, resourceDetailRoot: true, resourceScope: 'workspace-shared', activeMenu: 'workspace-knowledge' },
    children: [
      {
        path: '',
        name: 'workspace-shared-knowledge-library',
        redirect: { name: 'workspace-shared-knowledge-document-list' },
        meta: { title: '资料库', icon: 'icon-draft', order: 10 },
        children: [
          {
            path: 'document',
            name: 'workspace-shared-knowledge-document-list',
            component: () => import('@/views/knowledge-detail/document/index.vue'),
            meta: { title: '文档', order: 10 },
          },
        ],
      },
    ],
  },
]
