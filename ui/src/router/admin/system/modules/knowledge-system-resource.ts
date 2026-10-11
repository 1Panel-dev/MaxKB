import type { RouteRecordRaw } from 'vue-router'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'

/** System 知识库详情路由，由 System 汇总并继承系统布局。 */
export const systemResourceKnowledgeRoutes: RouteRecordRaw[] = [
  {
    path: '/system/resource/knowledge/:knowledgeId/:type',
    name: 'system-resource-knowledge-detail',
    component: () => import('@/views/knowledge-detail/index.vue'),
    redirect: { name: 'system-resource-knowledge-document-list' },
    meta: { title: '知识库详情', hidden: true, hideSidebar: true, resourceDetailRoot: true, scope: 'system', resourceScope: 'system-resource' },
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
            meta: { title: '文档', order: 10 },
          },
          {
            path: 'image',
            name: 'system-resource-knowledge-image-list',
            component: () => import('@/views/knowledge-detail/library/image/index.vue'),
            meta: { title: '图片', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.BASE },
          },
          {
            path: 'tag',
            name: 'system-resource-knowledge-tag',
            component: () => import('@/views/knowledge-detail/library/tags/index.vue'),
            meta: { title: '标签管理', order: 30 },
          },
        ],
      },
      {
        path: 'retrieval',
        name: 'system-resource-knowledge-retrieval',
        redirect: { name: 'system-resource-knowledge-recall-test' },
        meta: { title: '检索优化', icon: 'icon_trace_outlined', order: 30 },
        children: [
          {
            path: 'recall',
            name: 'system-resource-knowledge-recall-test',
            component: () => import('@/views/knowledge-detail/recall-test/index.vue'),
            meta: { title: '召回测试', order: 10 },
          },
          {
            path: 'question',
            name: 'system-resource-knowledge-question',
            component: () => import('@/views/knowledge-detail/question/index.vue'),
            meta: { title: '问题', order: 20 },
          },
          {
            path: 'dictionary',
            name: 'system-resource-knowledge-dictionary',
            component: () => import('@/views/knowledge-detail/dictionary/index.vue'),
            meta: { title: '自定义分词', order: 30 },
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
            meta: { title: '对话用户', order: 10 },
          },
          {
            path: 'external-retrieval',
            name: 'system-resource-knowledge-external-retrieval',
            component: () => import('@/views/knowledge-detail/external-retrieval/index.vue'),
            meta: { title: '外部检索服务', order: 20 },
          },
        ],
      },
      {
        path: 'setting',
        name: 'system-resource-knowledge-setting',
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
            meta: { title: '基础设置', order: 10 },
          },
          {
            path: 'setting/document-strategy',
            name: 'system-resource-knowledge-document-strategy',
            component: () => import('@/views/knowledge-detail/setting/document-strategy/index.vue'),
            meta: { title: '文档处理策略', order: 20, detailMenuVisible: (params) => params.type === KNOWLEDGE_TYPE_KEY.WEB },
          },
          {
            path: 'setting/scheduled-sync',
            name: 'system-resource-knowledge-scheduled-sync',
            component: () => import('@/views/knowledge-detail/setting/scheduled-sync/index.vue'),
            meta: { title: '定时同步', order: 30 },
          },
        ],
      },
    ],
  },
]
