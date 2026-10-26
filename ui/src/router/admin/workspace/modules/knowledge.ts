import type { RouteRecordRaw, RouteParamsGeneric } from 'vue-router'
import { canWorkspaceKnowledge } from '@/permission/modules/knowledge/workspace'
import { PermissionConstants as P } from '@/permission/core'
import type { Permission } from '@/permission/core/common'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'

function knowledgeAccess(permission: Permission, typeAllowed: (type: string) => boolean = () => true) {
  return (route: { params: RouteParamsGeneric }) => typeAllowed(String(route.params.type)) && canWorkspaceKnowledge(
    permission, String(route.params.knowledgeId), String(route.params.workspaceId),
  )
}

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
            meta: { title: '资料库', icon: 'icon-draft', order: 10 },
            children: [
              {
                path: 'document',
                name: 'workspace-knowledge-document-list',
                component: () => import('@/views/knowledge-detail/library/document/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_DOCUMENT_READ), next: 'workspace-knowledge-image-list', title: '文档', order: 10 },
              },
              {
                path: 'image',
                name: 'workspace-knowledge-image-list',
                component: () => import('@/views/knowledge-detail/library/image/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_IMAGE_READ, (type) => type === KNOWLEDGE_TYPE_KEY.BASE), next: 'workspace-knowledge-hit-test', title: '图片', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.BASE },
              },
              {
                path: 'tag',
                name: 'workspace-knowledge-tag',
                component: () => import('@/views/knowledge-detail/library/tags/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_TAG_READ), next: 'workspace-knowledge-dictionary', title: '标签管理', order: 30 },
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
            meta: { permission: knowledgeAccess(P.KNOWLEDGE_WORKFLOW_READ), next: 'workspace-knowledge-list', title: '工作流', icon: 'icon_ticket-flow_outlined', order: 20 },
          },
          {
            path: '',
            name: 'workspace-knowledge-retrieval',
            redirect: { name: 'workspace-knowledge-hit-test' },
            meta: { title: '检索优化', icon: 'icon_trace_outlined', order: 30 },
            children: [
              {
                path: 'hit-test',
                name: 'workspace-knowledge-hit-test',
                component: () => import('@/views/knowledge-detail/hit-test/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_HIT_TEST), next: 'workspace-knowledge-problem', title: '召回测试', order: 10 },
              },
              {
                path: 'problem',
                name: 'workspace-knowledge-problem',
                component: () => import('@/views/knowledge-detail/problem/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_PROBLEM_READ), next: 'workspace-knowledge-tag', title: '问题', order: 20 },
              },
              {
                path: 'dictionary',
                name: 'workspace-knowledge-dictionary',
                component: () => import('@/views/knowledge-detail/termbase/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_TERMBASE_READ), next: 'workspace-knowledge-chat-user', title: '自定义分词', order: 30 },
              },
            ],
          },
          {
            path: '',
            name: 'workspace-knowledge-integration',
            redirect: { name: 'workspace-knowledge-chat-user' },
            meta: { title: '授权与集成', icon: 'icon_personal-privacy_outlined', order: 40 },
            children: [
              {
                path: 'chat-user',
                name: 'workspace-knowledge-chat-user',
                component: () => import('@/views/knowledge-detail/chat-user/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_CHAT_USER_READ), next: 'workspace-knowledge-external-retrieval', title: '对话用户', order: 10 },
              },
              {
                path: 'external-retrieval',
                name: 'workspace-knowledge-external-retrieval',
                component: () => import('@/views/knowledge-detail/external-retrieval/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_EXTERNAL_SERVICE_READ), next: 'workspace-knowledge-setting', title: '外部检索服务', order: 20 },
              },
            ],
          },
          {
            path: 'setting',
            name: 'workspace-knowledge-setting',
            component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
            meta: { permission: knowledgeAccess(P.KNOWLEDGE_SETTING_READ, (type) => type === KNOWLEDGE_TYPE_KEY.BASE), next: 'workspace-knowledge-base-setting',
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
            name: 'workspace-knowledge-settings',
            redirect: (to) => ({ name: 'workspace-knowledge-base-setting', params: to.params, query: to.query, hash: to.hash }),
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
                name: 'workspace-knowledge-base-setting',
                component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_SETTING_READ, (type) => type !== KNOWLEDGE_TYPE_KEY.BASE), next: 'workspace-knowledge-document-strategy', title: '基础设置', order: 10 },
              },
              {
                path: 'setting/document-strategy',
                name: 'workspace-knowledge-document-strategy',
                component: () => import('@/views/knowledge-detail/setting/document-strategy/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_DOCUMENT_STRATEGY_READ, (type) => type === KNOWLEDGE_TYPE_KEY.WEB), next: 'workspace-knowledge-scheduled-sync', title: '文档处理策略', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.WEB },
              },
              {
                path: 'setting/scheduled-sync',
                name: 'workspace-knowledge-scheduled-sync',
                component: () => import('@/views/knowledge-detail/setting/scheduled-sync/index.vue'),
                meta: { permission: knowledgeAccess(P.KNOWLEDGE_SCHEDULED_SYNC_READ, (type) => type !== KNOWLEDGE_TYPE_KEY.BASE), next: 'workspace-knowledge-workflow', title: '定时同步', order: 30 },
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
