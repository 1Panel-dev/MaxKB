import { perm } from '@/permission'
import type { RouteRecordRaw, RouteParamsGeneric } from 'vue-router'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'

function firstAccessibleDetail(params: RouteParamsGeneric) {
  const system = perm.knowledge.system
  const candidates = [
    ['document-list', system.docRead()],
    ['image-list', params.type === KNOWLEDGE_TYPE_KEY.BASE && system.image.read()],
    ['hit-test', system.hitTest()],
    ['problem', system.problemRead()],
    ['tag', system.tagRead()],
    ['dictionary', system.termbaseRead()],
    ['chat-user', system.knowledgeChatUserRead()],
    ['external-retrieval', system.externalServiceRead()],
    [params.type === KNOWLEDGE_TYPE_KEY.BASE ? 'setting' : 'base-setting', system.settingRead()],
    ['document-strategy', params.type === KNOWLEDGE_TYPE_KEY.WEB && system.documentStrategyRead()],
    ['scheduled-sync', params.type !== KNOWLEDGE_TYPE_KEY.BASE && system.scheduledSyncRead()],
    ['workflow', system.debug()],
  ] as const
  const target = candidates.find(([, allowed]) => allowed)
  return { name: target ? `system-resource-knowledge-${target[0]}` : 'system-resource-knowledge', params }
}

/** System 知识库详情路由，由 System 汇总并继承系统布局。 */
export const systemResourceKnowledgeRoutes: RouteRecordRaw[] = [
  {
    path: '/system/resource/knowledge/:knowledgeId/:type',
    name: 'system-resource-knowledge-detail',
    component: () => import('@/views/knowledge-detail/index.vue'),
    redirect: (to) => firstAccessibleDetail(to.params),
    meta: { title: '知识库详情', hidden: true, resourceDetailRoot: true, scope: 'system', resourceScope: 'system-resource' },
    children: [
      {
        path: '',
        name: 'system-resource-knowledge-library',
        redirect: { name: 'system-resource-knowledge-document-list' },
        meta: { title: '资料库', icon: 'icon-draft', order: 10 },
        children: [
          {
            path: 'document',
            name: 'system-resource-knowledge-document-list',
            component: () => import('@/views/knowledge-detail/library/document/index.vue'),
            meta: { permission: () => perm.knowledge.system.docRead(), next: 'system-resource-knowledge', title: '文档', order: 10 },
          },
          {
            path: 'image',
            name: 'system-resource-knowledge-image-list',
            component: () => import('@/views/knowledge-detail/library/image/index.vue'),
            meta: { permission: () => perm.knowledge.system.image.read(), next: 'system-resource-knowledge', title: '图片', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.BASE },
          },
          {
            path: 'tag',
            name: 'system-resource-knowledge-tag',
            component: () => import('@/views/knowledge-detail/library/tags/index.vue'),
            meta: { permission: () => perm.knowledge.system.tagRead(), next: 'system-resource-knowledge', title: '标签管理', order: 30 },
          },
        ],
      },
      {
        path: 'workflow-entry',
        name: 'system-resource-knowledge-workflow',
        component: () => import('@/views/knowledge-detail/workflow-transform/index.vue'),
        beforeEnter: (to) => {
          if (to.params.type === KNOWLEDGE_TYPE_KEY.WORKFLOW) {
            return {
              name: 'system-resource-workflow-knowledge',
              params: { knowledgeId: to.params.knowledgeId },
              query: to.query,
              hash: to.hash,
            }
          }
        },
        meta: { permission: () => perm.knowledge.system.debug(), next: 'system-resource-knowledge', title: '工作流', icon: 'icon_ticket-flow_outlined', order: 20 },
      },
      {
        path: 'retrieval',
        name: 'system-resource-knowledge-retrieval',
        redirect: { name: 'system-resource-knowledge-hit-test' },
        meta: { title: '检索优化', icon: 'icon_trace_outlined', order: 30 },
        children: [
          {
            path: 'hit-test',
            name: 'system-resource-knowledge-hit-test',
            component: () => import('@/views/knowledge-detail/hit-test/index.vue'),
            meta: { permission: () => perm.knowledge.system.hitTest(), next: 'system-resource-knowledge', title: '召回测试', order: 10 },
          },
          {
            path: 'problem',
            name: 'system-resource-knowledge-problem',
            component: () => import('@/views/knowledge-detail/problem/index.vue'),
            meta: { permission: () => perm.knowledge.system.problemRead(), next: 'system-resource-knowledge', title: '问题', order: 20 },
          },
          {
            path: 'dictionary',
            name: 'system-resource-knowledge-dictionary',
            component: () => import('@/views/knowledge-detail/termbase/index.vue'),
            meta: { permission: () => perm.knowledge.system.termbaseRead(), next: 'system-resource-knowledge', title: '自定义分词', order: 30 },
          },
        ],
      },
      {
        path: 'integration',
        name: 'system-resource-knowledge-integration',
        redirect: { name: 'system-resource-knowledge-chat-user' },
        meta: { title: '授权与集成', icon: 'icon_personal-privacy_outlined', order: 40 },
        children: [
          {
            path: 'chat-user',
            name: 'system-resource-knowledge-chat-user',
            component: () => import('@/views/knowledge-detail/chat-user/index.vue'),
            meta: { permission: () => perm.knowledge.system.knowledgeChatUserRead(), next: 'system-resource-knowledge', title: '对话用户', order: 10 },
          },
          {
            path: 'external-retrieval',
            name: 'system-resource-knowledge-external-retrieval',
            component: () => import('@/views/knowledge-detail/external-retrieval/index.vue'),
            meta: { permission: () => perm.knowledge.system.externalServiceRead(), next: 'system-resource-knowledge', title: '外部检索服务', order: 20 },
          },
        ],
      },
      {
        path: 'setting',
        name: 'system-resource-knowledge-setting',
        component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
        meta: {
          permission: () => perm.knowledge.system.settingRead(),
          next: 'system-resource-knowledge',
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
        name: 'system-resource-knowledge-settings',
        redirect: (to) => ({ name: 'system-resource-knowledge-base-setting', params: to.params, query: to.query, hash: to.hash }),
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
            name: 'system-resource-knowledge-base-setting',
            component: () => import('@/views/knowledge-detail/setting/base/index.vue'),
            meta: { permission: () => perm.knowledge.system.settingRead(), next: 'system-resource-knowledge', title: '基础设置', order: 10 },
          },
          {
            path: 'setting/document-strategy',
            name: 'system-resource-knowledge-document-strategy',
            component: () => import('@/views/knowledge-detail/setting/document-strategy/index.vue'),
            meta: { permission: () => perm.knowledge.system.documentStrategyRead(), next: 'system-resource-knowledge', title: '文档处理策略', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.WEB },
          },
          {
            path: 'setting/scheduled-sync',
            name: 'system-resource-knowledge-scheduled-sync',
            component: () => import('@/views/knowledge-detail/setting/scheduled-sync/index.vue'),
            meta: { permission: () => perm.knowledge.system.scheduledSyncRead(), next: 'system-resource-knowledge', title: '定时同步', order: 30 },
          },
        ],
      },
    ],
  },
  {
    path: '/system/resource/knowledge/:knowledgeId/:type/document/:documentId',
    name: 'system-resource-knowledge-paragraph',
    component: () => import('@/views/document-detail/index.vue'),
    meta: { resourceScope: 'system-resource', scope: 'system', title: '文档分段', hidden: true, resourceDetailRoot: true },
  },
]
