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
        component: () => import('@/views/knowledge/index.vue'),
        meta: { title: '知识库列表', hidden: true },
      },
      {
        path: ':knowledgeId',
        name: 'workspace-knowledge-detail',
        component: () => import('@/views/knowledge-detail/index.vue'),
        redirect: { name: 'workspace-knowledge-document-list' },
        meta: { title: '知识库详情', hidden: true, resourceDetailRoot: true },
        children: [
          {
            path: '',
            name: 'workspace-knowledge-library',
            redirect: { name: 'workspace-knowledge-document-list' },
            meta: { title: '资料库', icon: 'icon-draft', order: 10 },
            children: [
              {
                path: 'document',
                name: 'workspace-knowledge-document-list',
                component: () => import('@/views/knowledge-detail/document/index.vue'),
                meta: { title: '文档', order: 10 },
              },
              {
                path: 'image',
                name: 'workspace-knowledge-image-list',
                component: () => import('@/views/knowledge-detail/image/index.vue'),
                meta: { title: '图片', order: 20 },
              },
              {
                path: 'tag',
                name: 'workspace-knowledge-tag',
                component: () => import('@/views/knowledge-detail/tag/index.vue'),
                meta: { title: '标签管理', order: 30 },
              },
            ],
          },
          {
            path: 'workflow-entry',
            name: 'workspace-knowledge-workflow',
            redirect: (to) => ({ name: 'workflow-knowledge', params: { workspaceId: to.params.workspaceId, knowledgeId: to.params.knowledgeId } }),
            meta: { title: '工作流', icon: 'icon_ticket-flow_outlined', order: 20 },
          },
          {
            path: 'retrieval',
            name: 'workspace-knowledge-retrieval',
            redirect: { name: 'workspace-knowledge-recall-test' },
            meta: { title: '检索优化', icon: 'icon_trace_outlined', order: 30 },
            children: [
              {
                path: 'recall',
                name: 'workspace-knowledge-recall-test',
                component: () => import('@/views/knowledge-detail/recall-test/index.vue'),
                meta: { title: '召回测试', order: 10 },
              },
              {
                path: 'question',
                name: 'workspace-knowledge-question',
                component: () => import('@/views/knowledge-detail/question/index.vue'),
                meta: { title: '问题', order: 20 },
              },
              {
                path: 'dictionary',
                name: 'workspace-knowledge-dictionary',
                component: () => import('@/views/knowledge-detail/dictionary/index.vue'),
                meta: { title: '自定义分词', order: 30 },
              },
            ],
          },
          {
            path: 'integration',
            name: 'workspace-knowledge-integration',
            redirect: { name: 'workspace-knowledge-chat-user' },
            meta: { title: '授权与集成', icon: 'icon_personal-privacy_outlined', order: 40 },
            children: [
              {
                path: 'chat-user',
                name: 'workspace-knowledge-chat-user',
                component: () => import('@/views/knowledge-detail/chat-user/index.vue'),
                meta: { title: '对话用户', order: 10 },
              },
              {
                path: 'external-retrieval',
                name: 'workspace-knowledge-external-retrieval',
                component: () => import('@/views/knowledge-detail/external-retrieval/index.vue'),
                meta: { title: '外部检索服务', order: 20 },
              },
            ],
          },
          {
            path: 'setting',
            name: 'workspace-knowledge-setting',
            component: () => import('@/views/knowledge-detail/setting/index.vue'),
            meta: { title: '设置', icon: 'icon_setting', activeIcon: 'icon_setting_filled', order: 50 },
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
