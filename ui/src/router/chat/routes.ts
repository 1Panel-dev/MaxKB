import type { RouteRecordRaw } from 'vue-router'

/** Chat 独立路由，后续的登录、对话分享页等统一在这里扩展。 */
export const chatRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'chat-home',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: { title: '对话' },
  },
]
