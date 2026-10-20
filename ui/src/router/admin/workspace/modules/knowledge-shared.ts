import type { RouteRecordRaw } from 'vue-router'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'

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
            component: () => import('@/views/knowledge-detail/library/document/index.vue'),
            meta: { title: '文档', order: 10 },
          },
          {
            path: 'image',
            name: 'workspace-shared-knowledge-image-list',
            component: () => import('@/views/knowledge-detail/library/image/index.vue'),
            meta: { title: '图片', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.BASE },
          },
          {
            path: 'tag',
            name: 'workspace-shared-knowledge-tag',
            component: () => import('@/views/knowledge-detail/library/tags/index.vue'),
            meta: { title: '标签管理', order: 30 },
          },
        ],
      },
      {
        path: 'workflow-entry',
        name: 'workspace-shared-knowledge-workflow',
        component: () => import('@/views/knowledge-detail/workflow-transform/index.vue'),
        beforeEnter: (to) => {
          if (to.params.type === KNOWLEDGE_TYPE_KEY.WORKFLOW) {
            return {
              name: 'workspace-shared-workflow-knowledge',
              params: { workspaceId: to.params.workspaceId, knowledgeId: to.params.knowledgeId },
              query: to.query,
              hash: to.hash,
            }
          }
        },
        meta: { title: '工作流', icon: 'icon_ticket-flow_outlined', order: 20 },
      },
      {
        path: 'retrieval',
        name: 'workspace-shared-knowledge-retrieval',
        redirect: { name: 'workspace-shared-knowledge-hit-test' },
        meta: { title: '检索优化', icon: 'icon_trace_outlined', order: 30 },
        children: [
          {
            path: 'hit-test',
            name: 'workspace-shared-knowledge-hit-test',
            component: () => import('@/views/knowledge-detail/hit-test/index.vue'),
            meta: { title: '召回测试', order: 10 },
          },
          {
            path: 'problem',
            name: 'workspace-shared-knowledge-problem',
            component: () => import('@/views/knowledge-detail/problem/index.vue'),
            meta: { title: '问题', order: 20 },
          },
          {
            path: 'dictionary',
            name: 'workspace-shared-knowledge-dictionary',
            component: () => import('@/views/knowledge-detail/termbase/index.vue'),
            meta: { title: '自定义分词', order: 30 },
          },
        ],
      },
      {
        path: 'integration',
        name: 'workspace-shared-knowledge-integration',
        redirect: { name: 'workspace-shared-knowledge-chat-user' },
        meta: { title: '授权与集成', icon: 'icon_personal-privacy_outlined', order: 40 },
        children: [
          {
            path: 'chat-user',
            name: 'workspace-shared-knowledge-chat-user',
            component: () => import('@/views/knowledge-detail/chat-user/index.vue'),
            meta: { title: '对话用户', order: 10 },
          },
          {
            path: 'external-retrieval',
            name: 'workspace-shared-knowledge-external-retrieval',
            component: () => import('@/views/knowledge-detail/external-retrieval/index.vue'),
            meta: { title: '外部检索服务', order: 20 },
          },
        ],
      },
      {
        path: 'setting',
        name: 'workspace-shared-knowledge-setting',
        component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
        meta: {
          title: '设置',
          icon: 'icon_setting',
          activeIcon: 'icon_setting_filled',
          order: 50,
          detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.BASE,
        },
      },
      {
        // 设置分组只提供菜单层级，子页面统一使用 setting 前缀。
        path: '',
        name: 'workspace-shared-knowledge-settings',
        redirect: (to) => ({ name: 'workspace-shared-knowledge-base-setting', params: to.params, query: to.query, hash: to.hash }),
        meta: {
          title: '设置',
          icon: 'icon_setting',
          activeIcon: 'icon_setting_filled',
          order: 50,
          detailMenuVisible: (params) => params.type !== KNOWLEDGE_TYPE_KEY.BASE,
        },
        children: [
          {
            path: 'setting/base',
            name: 'workspace-shared-knowledge-base-setting',
            component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
            meta: { title: '基础设置', order: 10 },
          },
          {
            path: 'setting/document-strategy',
            name: 'workspace-shared-knowledge-document-strategy',
            component: () => import('@/views/knowledge-detail/setting/document-strategy/index.vue'),
            meta: { title: '文档处理策略', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.WEB },
          },
          {
            path: 'setting/scheduled-sync',
            name: 'workspace-shared-knowledge-scheduled-sync',
            component: () => import('@/views/knowledge-detail/setting/scheduled-sync/index.vue'),
            meta: { title: '定时同步', order: 30 },
          },
        ],
      },
    ],
  },
  {
    path: 'shared/knowledge/:knowledgeId/:type/document/:documentId',
    name: 'workspace-shared-knowledge-paragraph',
    component: () => import('@/views/document-detail/index.vue'),
    meta: { resourceScope: 'workspace-shared', activeMenu: 'workspace-knowledge', title: '文档分段', hidden: true, resourceDetailRoot: true },
  },
]
