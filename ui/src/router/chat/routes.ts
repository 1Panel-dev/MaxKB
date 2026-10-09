import type { RouteRecordRaw } from 'vue-router'

const portalRoutes: RouteRecordRaw[] = [
    {
        path: '/portal',
        name: 'portal-home',
        component: () => import('@/views/portal/index.vue'),
        meta: { title: '门户', portal: true }
    },
    {
        path: '/portal/login',
        name: 'portal-login',
        component: () => import('@/views/chat/login/index.vue'),
        meta: { title: '登录', portal: true }
    },
    {
        path: '/portal/applications',
        name: 'portal-application-list',
        component: () => import('@/views/portal/index.vue'),
        meta: { title: '全部智能体', portal: true }
    },
    {
        path: '/portal/a/:applicationId',
        name: 'portal-application',
        component: () => import('@/views/portal/index.vue'),
        meta: { title: '对话', portal: true }
    },
    {
        path: '/portal/a/:applicationId/c/:chatId',
        name: 'portal-application-chat',
        component: () => import('@/views/portal/index.vue'),
        meta: { title: '对话', portal: true }
    }
]

 
const applicationRoutes: RouteRecordRaw[] = [
    {
        path: '/:accessToken/login',
        name: 'chat-login',
        component: () => import('@/views/chat/login/index.vue'),
        meta: { title: '登录' }
    },
    {
        path: '/:accessToken/',
        name: 'chat-home',
        component: () => import('@/views/chat/index.vue'),
        meta: { title: '应用对话' }
    },
    {
        path: '/:accessToken/c/:chatId',
        name: 'chat-home-detail',
        component: () => import('@/views/chat/index.vue'),
        meta: { title: '对话' }
    }
]

export const chatRoutes: RouteRecordRaw[] = [
    { path: '/', redirect: { name: 'portal-home' } },
    ...portalRoutes,
    ...applicationRoutes,
    {
        path: '/:pathMatch(.*)*',
        name: 'chat-not-found',
        component: () => import('@/views/chat/error/index.vue'),
        meta: { title: '页面不存在' }
    }
]
