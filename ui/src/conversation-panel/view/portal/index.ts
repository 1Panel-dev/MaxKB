import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConversationApi from '@/api/chat/conversation'
import PortalApi from '@/api/chat/portal'
import { createPortalConversationListStore, type PortalConversationListStore } from '../../left-sidebar/portal-conversation-list/index'
import { createChatConversation, type ChatConversationBundle, type ChatConversationRouting } from '../chat/index'

export interface PortalConversationBundle extends ChatConversationBundle {
  portalList: PortalConversationListStore
}

/** 门户对话：智能体 ID 取自路由，会话地址为 /portal/a/:applicationId/c/:chatId，新建对话为 /portal/a/:applicationId。 */
function usePortalChatRouting(): ChatConversationRouting {
  const route = useRoute()
  const router = useRouter()

  const getApplicationId = () => (typeof route.params.applicationId === 'string' ? route.params.applicationId : '')

  return {
    getApplicationId,
    getRouteChatId: () => (typeof route.params.chatId === 'string' ? route.params.chatId : ''),
    replaceChatId: (chatId) => {
      const applicationId = getApplicationId()
      // 门户首页与全部智能体页没有智能体，不同步会话地址
      if (!applicationId) return
      const { query } = route
      void router.replace(
        chatId
          ? { name: 'portal-application-chat', params: { applicationId, chatId }, query }
          : { name: 'portal-application', params: { applicationId }, query },
      )
    },
    getRouteQuery: () => route.query,
  }
}

/**
 * portal 模式:复用 chat 模式的会话装配，左侧改为按智能体分组的门户历史对话，主区域可切换为全部智能体。
 * 当前智能体的会话仍由会话列表 Store 维护，门户侧栏 Store 只管理分组、全部智能体与跨智能体导航。
 */
export interface PortalConversationOptions {
  /** 打开选择智能体抽屉，抽屉由门户视图渲染。 */
  openApplicationSelector: () => void
}

export function createPortalConversation(options: PortalConversationOptions): PortalConversationBundle {
  const route = useRoute()
  const router = useRouter()
  const routing = usePortalChatRouting()
  const bundle = createChatConversation(routing)
  const currentApplicationId = computed(routing.getApplicationId)
  const isApplicationListActive = computed(() => route.name === 'portal-application-list')

  // 门户内跳转保留地址栏参数，接口传参对后续打开的智能体同样生效
  const openApplication = (applicationId: string) => void router.push({ name: 'portal-application', params: { applicationId }, query: route.query })

  const portalList = createPortalConversationListStore({
    pageApplicationConversations: (page, size) => PortalApi.getPortalConversationPage(page, size),
    pageApplications: (page, size, name) => PortalApi.getPortalApplicationPage(page, size, name),
    pageGroupConversations: (applicationId, page, size) => ConversationApi.getPortalConversationPage(applicationId, page, size),
    removeConversation: (applicationId, chatId) => ConversationApi.deleteConversation(applicationId, chatId),
    currentApplicationId,
    isApplicationListActive,
    openApplication,
    openConversation: (applicationId, chatId) =>
      void router.push({ name: 'portal-application-chat', params: { applicationId, chatId }, query: route.query }),
    openApplicationList: () => void router.push({ name: 'portal-application-list', query: route.query }),
    openApplicationSelector: options.openApplicationSelector,
  })

  // 切换智能体时会话列表重新加载是异步的，此时列表仍是离开前智能体的会话：
  // 先把它写回离开的分组，再用进入分组已有的会话填充列表，避免侧栏先显示上一个智能体的会话。
  watch(currentApplicationId, (applicationId, previousApplicationId) => {
    const findGroup = (id: string) => portalList.applicationGroups.value.find((applicationGroup) => applicationGroup.id === id)
    const previousGroup = findGroup(previousApplicationId)
    if (previousGroup) previousGroup.conversations = [...bundle.list.conversations.value]
    bundle.list.conversations.value = [...(findGroup(applicationId)?.conversations ?? [])]
  })

  return { ...bundle, portalList }
}
