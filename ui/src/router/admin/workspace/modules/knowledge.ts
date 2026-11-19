import type { RouteRecordRaw } from 'vue-router'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { perm } from '@/permission'

export const knowledgeRoutes: RouteRecordRaw[] = [
  {
    path: 'knowledge',
    name: 'workspace-knowledge',
    redirect: { name: 'workspace-knowledge-list' },
    meta: {
      title: 'knowledge.title',
      activeMenu: 'workspace-knowledge',
      icon: 'icon_book_outlined',
      activeIcon: 'icon_book_filled',
      order: 30,
      permission: () => perm.knowledge.workspace.isShare(),
      next: 'workspace-tools',
    },
    children: [
      {
        path: '',
        name: 'workspace-knowledge-list',
        component: () => import('@/views/knowledge/index.vue'),
        meta: { title: 'knowledge.title', hidden: true },
      },

      {
        path: ':knowledgeId/:type',
        name: 'workspace-knowledge-detail',
        component: () => import('@/views/knowledge-detail/index.vue'),
        redirect: { name: 'workspace-knowledge-document-list' },
        meta: { title: '知识库详情', hidden: true, resourceDetailRoot: true },
        children: [
          {
            path: '',
            name: 'workspace-knowledge-library',
            redirect: { name: 'workspace-knowledge-document-list' },
            meta: { title: 'knowledge.menu.library', icon: 'icon-draft', order: 10 },
            children: [
              {
                path: 'document',
                name: 'workspace-knowledge-document-list',
                component: () => import('@/views/knowledge-detail/library/document/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.docRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-image-list',
                  title: 'knowledge.document.title',
                  order: 10,
                },
              },
              {
                path: 'image',
                name: 'workspace-knowledge-image-list',
                component: () => import('@/views/knowledge-detail/library/image/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.image.read(String(params.knowledgeId)),
                  next: 'workspace-knowledge-tag',
                  title: 'knowledge.image.title',
                  order: 20,
                  detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.BASE || params.type === KNOWLEDGE_TYPE_KEY.WORKFLOW,
                },
              },
              {
                path: 'tag',
                name: 'workspace-knowledge-tag',
                component: () => import('@/views/knowledge-detail/library/tags/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.tagRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-workflow',
                  title: 'knowledge.tags.title',
                  order: 30,
                },
              },
            ],
          },
          {
            path: 'workflow-entry',
            name: 'workspace-knowledge-workflow',
            component: () => import('@/views/knowledge-detail/workflow-transform/index.vue'),
            beforeEnter: (to) => {
              if (to.params.type === KNOWLEDGE_TYPE_KEY.WORKFLOW) {
                return {
                  name: 'workflow-knowledge',
                  params: { workspaceId: to.params.workspaceId, knowledgeId: to.params.knowledgeId },
                  query: to.query,
                  hash: to.hash,
                }
              }
            },
            meta: {
              permission: ({ params }) => perm.knowledge.workspace.debug(String(params.knowledgeId)),
              next: 'workspace-knowledge-hit-test',
              title: 'knowledge.workflow.title',
              icon: 'icon_ticket-flow_outlined',
              order: 20,
            },
          },
          {
            path: '',
            name: 'workspace-knowledge-retrieval',
            redirect: { name: 'workspace-knowledge-hit-test' },
            meta: { title: 'knowledge.menu.retrieval', icon: 'icon_trace_outlined', order: 30 },
            children: [
              {
                path: 'hit-test',
                name: 'workspace-knowledge-hit-test',
                component: () => import('@/views/knowledge-detail/hit-test/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.hitTest(String(params.knowledgeId)),
                  next: 'workspace-knowledge-problem',
                  title: 'knowledge.hitTest.title',
                  order: 10,
                },
              },
              {
                path: 'problem',
                name: 'workspace-knowledge-problem',
                component: () => import('@/views/knowledge-detail/problem/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.problemRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-dictionary',
                  title: 'knowledge.question.title',
                  order: 20,
                },
              },
              {
                path: 'dictionary',
                name: 'workspace-knowledge-dictionary',
                component: () => import('@/views/knowledge-detail/termbase/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.termbaseRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-chat-user',
                  title: 'knowledge.termbase.title',
                  order: 30,
                },
              },
            ],
          },
          {
            path: '',
            name: 'workspace-knowledge-integration',
            redirect: { name: 'workspace-knowledge-chat-user' },
            meta: { title: 'knowledge.menu.integration', icon: 'icon_personal-privacy_outlined', order: 40 },
            children: [
              {
                path: 'chat-user',
                name: 'workspace-knowledge-chat-user',
                component: () => import('@/views/knowledge-detail/chat-user/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.knowledgeChatUserRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-external-retrieval',
                  title: 'authorization.chatUser.title',
                  order: 10,
                },
              },
              {
                path: 'external-retrieval',
                name: 'workspace-knowledge-external-retrieval',
                component: () => import('@/views/knowledge-detail/external-retrieval/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.externalServiceRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-setting',
                  title: 'knowledge.externalRetrieval.title',
                  order: 20,
                },
              },
            ],
          },
          {
            path: 'setting',
            name: 'workspace-knowledge-setting',
            component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
            meta: {
              permission: ({ params }) => perm.knowledge.workspace.settingRead(String(params.knowledgeId)),
              next: 'workspace-knowledge-settings',
              title: 'common.labels.settings',
              icon: 'icon_setting',
              activeIcon: 'icon_setting_filled',
              order: 50,
              detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.BASE,
            },
          },
          {
            // 设置分组只提供菜单层级，子页面统一使用 setting 前缀。
            path: '',
            name: 'workspace-knowledge-settings',
            redirect: (to) => ({ name: 'workspace-knowledge-base-setting', params: to.params, query: to.query, hash: to.hash }),
            meta: {
              title: 'common.labels.settings',
              icon: 'icon_setting',
              activeIcon: 'icon_setting_filled',
              order: 50,
              detailMenuVisible: (params) => params.type !== KNOWLEDGE_TYPE_KEY.BASE,
            },
            children: [
              {
                path: 'setting/base',
                name: 'workspace-knowledge-base-setting',
                component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.settingRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-document-strategy',
                  title: 'knowledge.baseSettings.title',
                  order: 10,
                },
              },
              {
                path: 'setting/document-strategy',
                name: 'workspace-knowledge-document-strategy',
                component: () => import('@/views/knowledge-detail/setting/document-strategy/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.documentStrategyRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-scheduled-sync',
                  title: 'knowledge.documentStrategy.title',
                  order: 20,
                  detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.WEB,
                },
              },
              {
                path: 'setting/scheduled-sync',
                name: 'workspace-knowledge-scheduled-sync',
                component: () => import('@/views/knowledge-detail/setting/scheduled-sync/index.vue'),
                meta: {
                  permission: ({ params }) => perm.knowledge.workspace.scheduledSyncRead(String(params.knowledgeId)),
                  next: 'workspace-knowledge-document-list',
                  title: 'knowledge.scheduledSync.title',
                  order: 30,
                },
              },
            ],
          },
        ],
      },
      {
        path: ':knowledgeId/:type/document/:documentId',
        name: 'workspace-knowledge-paragraph',
        component: () => import('@/views/document-detail/index.vue'),
        meta: { title: '文档分段', hidden: true, resourceDetailRoot: true },
      },
    ],
  },
]
