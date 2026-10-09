import { inject, ref, type InjectionKey, type Ref } from 'vue'
import type { ChatApplicationProfile, PortalApplicationConversations } from '@/api/types'
import type { Conversation } from '../../core/types'

/** 门户侧栏中按智能体分组的历史对话。 */
export interface PortalApplicationGroup {
  id: string
  name: string
  icon: string
  conversations: Conversation[]
  expanded: boolean
}

// 由 Portal 入口注入本组件需要的接口与导航。
export interface PortalConversationListDeps {
  pageApplicationConversations: (page: number, size: number) => Promise<{ records?: PortalApplicationConversations[] }>
  pageApplications: (page: number, size: number, name: string) => Promise<{ records?: ChatApplicationProfile[] }>
  /** 分页获取某个智能体的历史会话，展开分组时刷新。 */
  pageGroupConversations: (applicationId: string, page: number, size: number) => Promise<{ records?: Conversation[] } | null | undefined>
  removeConversation: (applicationId: string, chatId: string) => Promise<unknown>
  /** 当前对话的智能体 ID；门户首页与全部智能体页为空。 */
  currentApplicationId: Readonly<Ref<string>>
  /** 当前是否处于全部智能体页。 */
  isApplicationListActive: Readonly<Ref<boolean>>
  /** 打开智能体的新建对话。 */
  openApplication: (applicationId: string) => void
  /** 打开其他智能体的会话。 */
  openConversation: (applicationId: string, chatId: string) => void
  /** 打开全部智能体页。 */
  openApplicationList: () => void
  /** 打开选择智能体抽屉。 */
  openApplicationSelector: () => void
}

// 门户可访问的智能体数量有限，一次加载全部
const APPLICATION_PAGE_SIZE = 100
// 每个智能体分组最多展示最近 5 条会话
const GROUP_CONVERSATION_LIMIT = 5

/**
 * 管理门户侧栏的智能体分组与全部智能体列表。当前智能体的会话由会话列表 Store 维护，
 * 侧栏展示时以其为准，保证新建、重命名和删除即时生效；其他智能体使用分组接口返回的最近会话。
 */
export function createPortalConversationListStore(deps: PortalConversationListDeps) {
  const { pageApplicationConversations, pageApplications, pageGroupConversations, removeConversation, currentApplicationId } = deps

  // 历史对话分组
  const applicationGroups = ref<PortalApplicationGroup[]>([])
  const isApplicationGroupsLoaded = ref(false)

  const loadApplicationGroups = () =>
    pageApplicationConversations(1, APPLICATION_PAGE_SIZE).then((response) => {
      applicationGroups.value = (response.records ?? []).map((application) => ({
        ...application,
        expanded: application.conversations.length > 0 || application.id === currentApplicationId.value,
      }))
      isApplicationGroupsLoaded.value = true
    })

  // 展开其他智能体时查询其最近会话；当前智能体以会话列表 Store 为准，无需查询
  const loadGroupConversations = (group: PortalApplicationGroup) =>
    pageGroupConversations(group.id, 1, GROUP_CONVERSATION_LIMIT)
      .then((response) => {
        group.conversations = response?.records ?? []
      })
      .catch(() => {
        // 查询失败时保留分组接口返回的会话
      })

  const toggleGroup = (applicationId: string) => {
    const group = applicationGroups.value.find((applicationGroup) => applicationGroup.id === applicationId)
    if (!group) return
    group.expanded = !group.expanded
    if (group.expanded && group.id !== currentApplicationId.value) loadGroupConversations(group)
  }

  // 删除其他智能体的会话：请求成功后更新本地分组
  const deleteGroupConversation = async (applicationId: string, chatId: string) => {
    await removeConversation(applicationId, chatId)
    const group = applicationGroups.value.find((applicationGroup) => applicationGroup.id === applicationId)
    if (group) group.conversations = group.conversations.filter((conversation) => conversation.id !== chatId)
  }

  // 按名称查询可访问的智能体，全部智能体页与选择智能体抽屉各自维护搜索条件与结果
  const fetchApplications = (keyword: string) =>
    pageApplications(1, APPLICATION_PAGE_SIZE, keyword.trim()).then((response) => response.records ?? [])

  // 全部智能体页
  const applications = ref<ChatApplicationProfile[]>([])
  const applicationKeyword = ref('')
  const isApplicationsLoading = ref(false)

  const loadApplications = () => {
    isApplicationsLoading.value = true
    return fetchApplications(applicationKeyword.value)
      .then((records) => {
        applications.value = records
      })
      .finally(() => {
        isApplicationsLoading.value = false
      })
  }

  // 新建对话：进入当前智能体的新建对话地址，会话 ID 同步随之新建；没有当前智能体时选择智能体
  const newConversation = () => {
    if (currentApplicationId.value) deps.openApplication(currentApplicationId.value)
    else deps.openApplicationSelector()
  }

  return {
    applicationGroups,
    isApplicationGroupsLoaded,
    loadApplicationGroups,
    toggleGroup,
    deleteGroupConversation,
    applications,
    applicationKeyword,
    isApplicationsLoading,
    loadApplications,
    fetchApplications,
    currentApplicationId,
    isApplicationListActive: deps.isApplicationListActive,
    openApplication: deps.openApplication,
    openConversation: deps.openConversation,
    openApplicationList: deps.openApplicationList,
    newConversation,
  }
}

export type PortalConversationListStore = ReturnType<typeof createPortalConversationListStore>

// 门户视图内共享 Store
export const PORTAL_CONVERSATION_LIST_KEY: InjectionKey<PortalConversationListStore> = Symbol('portal-conversation-list')

export function usePortalConversationListStore(): PortalConversationListStore {
  const store = inject(PORTAL_CONVERSATION_LIST_KEY)
  if (!store) throw new Error('usePortalConversationListStore 必须在门户会话视图内使用')
  return store
}
