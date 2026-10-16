/** 知识库详情的资源范围、API 装配与详情数据共享。 */
import { computed, inject, provide, reactive, watch, type ComputedRef, type InjectionKey } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MsgWarning } from '@/utils/message'
import { getResourceScope, isWorkspaceResource, isWorkspaceSharedResource } from '@/utils/resource-context'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedKnowledgeApi from '@/api/admin/workspace/shared/knowledge/knowledge'
import SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import ImageApi from '@/api/admin/workspace/knowledge/image'
import SystemResourceImageApi from '@/api/admin/system/resource-management/knowledge/image'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import SharedDocumentApi from '@/api/admin/workspace/shared/knowledge/document'
import SystemResourceDocumentApi from '@/api/admin/system/resource-management/knowledge/document'
import SystemSharedDocumentApi from '@/api/admin/system/shared-resources/knowledge/document'
import ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import SharedParagraphApi from '@/api/admin/workspace/shared/knowledge/paragraph'
import SystemResourceParagraphApi from '@/api/admin/system/resource-management/knowledge/paragraph'
import SystemSharedParagraphApi from '@/api/admin/system/shared-resources/knowledge/paragraph'
import TagsApi from '@/api/admin/workspace/knowledge/tags'
import SharedTagsApi from '@/api/admin/workspace/shared/knowledge/tags'
import SystemResourceTagsApi from '@/api/admin/system/resource-management/knowledge/tags'
import SystemSharedTagsApi from '@/api/admin/system/shared-resources/knowledge/tags'
import TermbaseApi from '@/api/admin/workspace/knowledge/termbase'
import SharedTermbaseApi from '@/api/admin/workspace/shared/knowledge/termbase'
import SystemResourceTermbaseApi from '@/api/admin/system/resource-management/knowledge/termbase'
import SystemSharedTermbaseApi from '@/api/admin/system/shared-resources/knowledge/termbase'
import ProblemApi from '@/api/admin/workspace/knowledge/problem'
import SharedProblemApi from '@/api/admin/workspace/shared/knowledge/problem'
import SystemResourceProblemApi from '@/api/admin/system/resource-management/knowledge/problem'
import SystemSharedProblemApi from '@/api/admin/system/shared-resources/knowledge/problem'
import WorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import ScheduledSyncApi from '@/api/admin/workspace/knowledge/scheduled-sync'
import SharedScheduledSyncApi from '@/api/admin/workspace/shared/knowledge/scheduled-sync'
import SystemResourceScheduledSyncApi from '@/api/admin/system/resource-management/knowledge/scheduled-sync'
import SystemSharedScheduledSyncApi from '@/api/admin/system/shared-resources/knowledge/scheduled-sync'
import ExternalRetrievalApi from '@/api/admin/workspace/knowledge/external-retrieval'
import SharedExternalRetrievalApi from '@/api/admin/workspace/shared/knowledge/external-retrieval'
import SystemResourceExternalRetrievalApi from '@/api/admin/system/resource-management/knowledge/external-retrieval'
import SystemSharedExternalRetrievalApi from '@/api/admin/system/shared-resources/knowledge/external-retrieval'
import ChatUserApi from '@/api/admin/workspace/chat-user'
import SharedChatUserApi from '@/api/admin/workspace/shared/chat-user'
import SystemResourceChatUserApi from '@/api/admin/system/resource-management/chat-user'
import SystemSharedChatUserApi from '@/api/admin/system/shared-resources/chat-user'
import type { KnowledgeDetail } from '@/api/types'
import type { ResourceScope } from '@/router/admin/types'

/** 共有方法保持必填，仅部分范围提供的方法按真实缺失情况标记为可选。 */
type ApiKeys<Api> = Api extends unknown ? keyof Api : never
type OptionalApiMethods<Api> = Pick<Api, keyof Api> & {
  [Method in Exclude<ApiKeys<Api>, keyof Api>]?: Api extends unknown ? (Method extends keyof Api ? Api[Method] : never) : never
}

interface KnowledgeResourceApi {
  readonly paragraph: OptionalApiMethods<
    typeof ParagraphApi | typeof SharedParagraphApi | typeof SystemResourceParagraphApi | typeof SystemSharedParagraphApi
  >
  readonly problem: OptionalApiMethods<typeof ProblemApi | typeof SharedProblemApi | typeof SystemResourceProblemApi | typeof SystemSharedProblemApi>
  readonly chatUser: OptionalApiMethods<
    typeof ChatUserApi | typeof SharedChatUserApi | typeof SystemResourceChatUserApi | typeof SystemSharedChatUserApi
  >
  readonly image?: OptionalApiMethods<typeof ImageApi | typeof SystemResourceImageApi>
  readonly workflow?: typeof WorkflowApi
  readonly document: OptionalApiMethods<
    typeof DocumentApi | typeof SharedDocumentApi | typeof SystemResourceDocumentApi | typeof SystemSharedDocumentApi
  >
  readonly tags: OptionalApiMethods<typeof TagsApi | typeof SharedTagsApi | typeof SystemResourceTagsApi | typeof SystemSharedTagsApi>
  readonly termbase: OptionalApiMethods<
    typeof TermbaseApi | typeof SharedTermbaseApi | typeof SystemResourceTermbaseApi | typeof SystemSharedTermbaseApi
  >
  readonly knowledge: typeof KnowledgeApi | typeof SharedKnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi
  readonly scheduledSync: OptionalApiMethods<
    typeof ScheduledSyncApi | typeof SharedScheduledSyncApi | typeof SystemResourceScheduledSyncApi | typeof SystemSharedScheduledSyncApi
  >
  readonly externalRetrieval: OptionalApiMethods<
    | typeof ExternalRetrievalApi
    | typeof SharedExternalRetrievalApi
    | typeof SystemResourceExternalRetrievalApi
    | typeof SystemSharedExternalRetrievalApi
  >
}

interface KnowledgeResourceConfig {
  resourceApi: KnowledgeResourceApi
  listRouteName: string
}

/** 仅配置真实存在的完整 API 对象；缺失模块不回退到 Workspace。 */
const resourceConfigs = {
  workspace: {
    resourceApi: {
      chatUser: ChatUserApi,
      knowledge: KnowledgeApi,
      scheduledSync: ScheduledSyncApi,
      externalRetrieval: ExternalRetrievalApi,
      document: DocumentApi,
      paragraph: ParagraphApi,
      image: ImageApi,
      tags: TagsApi,
      termbase: TermbaseApi,
      problem: ProblemApi,
      workflow: WorkflowApi,
    },
    listRouteName: 'workspace-knowledge-list',
  },
  'workspace-shared': {
    resourceApi: {
      chatUser: SharedChatUserApi,
      knowledge: SharedKnowledgeApi,
      scheduledSync: SharedScheduledSyncApi,
      externalRetrieval: SharedExternalRetrievalApi,
      document: SharedDocumentApi,
      paragraph: SharedParagraphApi,
      tags: SharedTagsApi,
      termbase: SharedTermbaseApi,
      problem: SharedProblemApi,
    },
    listRouteName: 'workspace-knowledge-list',
  },
  'system-resource': {
    resourceApi: {
      chatUser: SystemResourceChatUserApi,
      knowledge: SystemResourceKnowledgeApi,
      scheduledSync: SystemResourceScheduledSyncApi,
      externalRetrieval: SystemResourceExternalRetrievalApi,
      document: SystemResourceDocumentApi,
      paragraph: SystemResourceParagraphApi,
      image: SystemResourceImageApi,
      tags: SystemResourceTagsApi,
      termbase: SystemResourceTermbaseApi,
      problem: SystemResourceProblemApi,
    },
    listRouteName: 'system-resource-knowledge',
  },
  'system-shared': {
    resourceApi: {
      chatUser: SystemSharedChatUserApi,
      knowledge: SystemSharedKnowledgeApi,
      scheduledSync: SystemSharedScheduledSyncApi,
      externalRetrieval: SystemSharedExternalRetrievalApi,
      document: SystemSharedDocumentApi,
      paragraph: SystemSharedParagraphApi,
      tags: SystemSharedTagsApi,
      termbase: SystemSharedTermbaseApi,
      problem: SystemSharedProblemApi,
    },
    listRouteName: 'system-shared-knowledge',
  },
} satisfies Record<ResourceScope, KnowledgeResourceConfig>

interface KnowledgeDetailState {
  knowledge: ComputedRef<KnowledgeDetail | undefined>
  replaceKnowledgeDetail: (knowledge: KnowledgeDetail) => void
}

interface KnowledgeDetailContext extends KnowledgeDetailState {
  knowledgeId: ComputedRef<string>
  resourceApi: KnowledgeResourceApi
  listRouteName: ComputedRef<string>
  routeNames: ComputedRef<{ detail: string; document: string; paragraph: string; workflowEntry: string; workflow: string }>
  routeParams: ComputedRef<{ knowledgeId: string; workspaceId?: string | string[] }>
}

function createKnowledgeDetailContext(state: KnowledgeDetailState): KnowledgeDetailContext {
  const route = useRoute()
  const resourceScope = computed(() => route.meta.resourceScope)
  const resourceConfig = computed<KnowledgeResourceConfig>(() => {
    const scope = resourceScope.value
    if (!scope) throw new Error('Knowledge detail resource scope is unavailable')
    return resourceConfigs[scope]
  })
  // 保持接口入口稳定，通过 getter 在路由范围变化时读取当前配置。
  const resourceApi = reactive({
    get chatUser() {
      return resourceConfig.value.resourceApi.chatUser
    },
    get workflow() {
      return resourceConfig.value.resourceApi.workflow
    },
    get image() {
      return resourceConfig.value.resourceApi.image
    },
    get document() {
      return resourceConfig.value.resourceApi.document
    },
    get paragraph() {
      return resourceConfig.value.resourceApi.paragraph
    },
    get tags() {
      return resourceConfig.value.resourceApi.tags
    },
    get termbase() {
      return resourceConfig.value.resourceApi.termbase
    },
    get problem() {
      return resourceConfig.value.resourceApi.problem
    },
    get knowledge() {
      return resourceConfig.value.resourceApi.knowledge
    },
    get scheduledSync() {
      return resourceConfig.value.resourceApi.scheduledSync
    },
    get externalRetrieval() {
      return resourceConfig.value.resourceApi.externalRetrieval
    },
  })
  const routeNames = computed(() => {
    const scope = resourceScope.value
    if (!scope) throw new Error('Knowledge resource scope is unavailable')
    const prefix = `${scope}-knowledge`
    return {
      detail: `${prefix}-detail`,
      document: `${prefix}-document-list`,
      paragraph: `${prefix}-paragraph`,
      workflowEntry: `${prefix}-workflow`,
      workflow: isWorkspaceResource() ? 'workflow-knowledge' : `${scope}-workflow-knowledge`,
    }
  })
  const routeParams = computed(() => {
    const knowledgeId = String(route.params.knowledgeId ?? '')
    return isWorkspaceResource() || isWorkspaceSharedResource() ? { workspaceId: route.params.workspaceId, knowledgeId } : { knowledgeId }
  })
  return {
    ...state,
    routeNames,
    routeParams,
    knowledgeId: computed(() => String(route.params.knowledgeId ?? '')),
    resourceApi,
    listRouteName: computed(() => resourceConfig.value.listRouteName),
  }
}

const knowledgeDetailContextKey: InjectionKey<KnowledgeDetailContext> = Symbol('knowledge-detail-context')

export function provideKnowledgeDetailContext(state: KnowledgeDetailState) {
  const context = createKnowledgeDetailContext(state)
  provide(knowledgeDetailContextKey, context)
  return context
}

/** 根据消费方声明的范围，从现有完整 API 对象推导类型，不补造方法。 */
type ScopedResourceApi<Scope extends ResourceScope> = {
  readonly [Module in keyof KnowledgeResourceApi]: Scope extends ResourceScope
    ? Module extends keyof (typeof resourceConfigs)[Scope]['resourceApi']
      ? (typeof resourceConfigs)[Scope]['resourceApi'][Module]
      : undefined
    : never
}

type ScopedKnowledgeDetailContext<Scope extends ResourceScope> = Omit<KnowledgeDetailContext, 'resourceApi'> & {
  resourceApi: Omit<
    ScopedResourceApi<Scope>,
    'scheduledSync' | 'tags' | 'termbase' | 'problem' | 'document' | 'chatUser' | 'externalRetrieval' | 'image'
  > & {
    readonly problem: OptionalApiMethods<(typeof resourceConfigs)[Scope]['resourceApi']['problem']>
    readonly image: KnowledgeResourceApi['image']
    readonly chatUser: OptionalApiMethods<(typeof resourceConfigs)[Scope]['resourceApi']['chatUser']>
    readonly scheduledSync: OptionalApiMethods<(typeof resourceConfigs)[Scope]['resourceApi']['scheduledSync']>
    readonly tags: OptionalApiMethods<(typeof resourceConfigs)[Scope]['resourceApi']['tags']>
    readonly termbase: OptionalApiMethods<(typeof resourceConfigs)[Scope]['resourceApi']['termbase']>
    readonly document: OptionalApiMethods<(typeof resourceConfigs)[Scope]['resourceApi']['document']>
    readonly externalRetrieval: OptionalApiMethods<(typeof resourceConfigs)[Scope]['resourceApi']['externalRetrieval']>
  }
}

export function useKnowledgeDetailContext<const Scope extends ResourceScope = ResourceScope>(options?: {
  resourceScopes: readonly Scope[]
}): ScopedKnowledgeDetailContext<Scope> {
  const context = inject(knowledgeDetailContextKey)
  if (!context) throw new Error('Knowledge detail context is unavailable')
  if (!options) return context as ScopedKnowledgeDetailContext<Scope>
  const resourceScopes: readonly ResourceScope[] = options.resourceScopes

  const router = useRouter()
  const route = useRoute()
  // 消费方仅声明范围；不支持的来源由上下文提示并返回当前来源的文档页。
  watch(
    getResourceScope,
    (scope) => {
      if (!scope || resourceScopes.includes(scope)) return
      MsgWarning('当前资源范围不支持此操作')
      void router.replace({
        name: context.routeNames.value.document,
        params: { ...context.routeParams.value, type: route.params.type },
        query: route.query,
        hash: route.hash,
      })
    },
    { immediate: true },
  )

  // 每次读取仍验证当前范围，防止跳转完成前或切换范围后访问不支持的 API。
  const resourceApi = new Proxy(context.resourceApi, {
    get(target, module, receiver) {
      const scope = getResourceScope()
      if (!scope || !resourceScopes.includes(scope)) {
        throw new Error('Knowledge detail resource scope is unsupported for this operation')
      }
      return Reflect.get(target, module, receiver)
    },
  })
  return { ...context, resourceApi } as ScopedKnowledgeDetailContext<Scope>
}
