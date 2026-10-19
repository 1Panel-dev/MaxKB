/** 智能体详情的资源范围、API 装配与详情数据共享。 */
import { computed, inject, provide, reactive, type ComputedRef, type InjectionKey } from 'vue'
import { useRoute } from 'vue-router'
import ApplicationApi from '@/api/admin/workspace/application/application'
import SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import ChatUserApi from '@/api/admin/workspace/chat-user'
import SystemResourceChatUserApi from '@/api/admin/system/resource-management/chat-user'
import OverviewApi from '@/api/admin/workspace/application/overview'
import SystemResourceOverviewApi from '@/api/admin/system/resource-management/application/overview'
import AccessApi from '@/api/admin/workspace/application/access'
import SystemResourceAccessApi from '@/api/admin/system/resource-management/application/access'
import ChatLogApi from '@/api/admin/workspace/application/chat-log'
import SystemResourceChatLogApi from '@/api/admin/system/resource-management/application/chat-log'
import WorkflowApi from '@/api/admin/workspace/application/workflow'
import SystemResourceWorkflowApi from '@/api/admin/system/resource-management/application/workflow'
import type { ApplicationDetail } from '@/api/types'
import type { ResourceScope } from '@/router/admin/types'

type ApplicationResourceScope = Extract<ResourceScope, 'workspace' | 'system-resource'>

/** 共有方法保持必填，仅部分范围提供的方法按真实缺失情况标记为可选。 */
type ApiKeys<Api> = Api extends unknown ? keyof Api : never
type OptionalApiMethods<Api> = Pick<Api, keyof Api> & {
  [Method in Exclude<ApiKeys<Api>, keyof Api>]?: Api extends unknown ? (Method extends keyof Api ? Api[Method] : never) : never
}

interface ApplicationResourceApi {
  readonly application: OptionalApiMethods<typeof ApplicationApi | typeof SystemResourceApplicationApi>
  readonly chatUser: typeof ChatUserApi | typeof SystemResourceChatUserApi
  readonly overview: typeof OverviewApi | typeof SystemResourceOverviewApi
  readonly access: typeof AccessApi | typeof SystemResourceAccessApi
  readonly chatLog: typeof ChatLogApi | typeof SystemResourceChatLogApi
  readonly workflow: typeof WorkflowApi | typeof SystemResourceWorkflowApi
}

export type ApplicationChatLogApi = ApplicationResourceApi['chatLog']

interface ApplicationResourceConfig {
  resourceApi: ApplicationResourceApi
  listRouteName: string
}

/** 仅装配真实存在的完整 API 对象，按当前资源范围选择对应实现。 */
const resourceConfigs = {
  workspace: {
    resourceApi: {
      application: ApplicationApi,
      chatUser: ChatUserApi,
      overview: OverviewApi,
      access: AccessApi,
      chatLog: ChatLogApi,
      workflow: WorkflowApi,
    },
    listRouteName: 'workspace-application-list',
  },
  'system-resource': {
    resourceApi: {
      application: SystemResourceApplicationApi,
      chatUser: SystemResourceChatUserApi,
      overview: SystemResourceOverviewApi,
      access: SystemResourceAccessApi,
      chatLog: SystemResourceChatLogApi,
      workflow: SystemResourceWorkflowApi,
    },
    listRouteName: 'system-resource-applications',
  },
} satisfies Record<ApplicationResourceScope, ApplicationResourceConfig>

interface ApplicationDetailState {
  application: ComputedRef<ApplicationDetail | undefined>
  /** showLoading 默认 true；传 false 不修改整页加载状态。 */
  refreshApplicationDetail: (showLoading?: boolean) => Promise<void>
  replaceApplicationDetail: (applicationDetail: ApplicationDetail) => void
}

interface ApplicationDetailContext extends ApplicationDetailState {
  applicationId: ComputedRef<string>
  resourceApi: ApplicationResourceApi
  listRouteName: ComputedRef<string>
  routeParams: ComputedRef<{ applicationId: string; workspaceId?: string | string[] }>
}

function createApplicationDetailContext(state: ApplicationDetailState): ApplicationDetailContext {
  const route = useRoute()
  const resourceConfig = computed<ApplicationResourceConfig>(() => {
    const scope = route.meta.resourceScope
    if (scope !== 'workspace' && scope !== 'system-resource') throw new Error('Application detail resource scope is unavailable')
    return resourceConfigs[scope]
  })
  // 保持接口入口稳定，在读取时选择当前路由范围的配置。
  const resourceApi = reactive({
    get application() {
      return resourceConfig.value.resourceApi.application
    },
    get chatUser() {
      return resourceConfig.value.resourceApi.chatUser
    },
    get overview() {
      return resourceConfig.value.resourceApi.overview
    },
    get access() {
      return resourceConfig.value.resourceApi.access
    },
    get chatLog() {
      return resourceConfig.value.resourceApi.chatLog
    },
    get workflow() {
      return resourceConfig.value.resourceApi.workflow
    },
  })
  const applicationId = computed(() => String(route.params.applicationId ?? ''))
  return {
    ...state,
    applicationId,
    resourceApi,
    listRouteName: computed(() => resourceConfig.value.listRouteName),
    routeParams: computed(() =>
      route.meta.resourceScope === 'workspace'
        ? { workspaceId: route.params.workspaceId, applicationId: applicationId.value }
        : { applicationId: applicationId.value },
    ),
  }
}

const applicationDetailContextKey: InjectionKey<ApplicationDetailContext> = Symbol('application-detail-context')

export function provideApplicationDetailContext(state: ApplicationDetailState) {
  const context = createApplicationDetailContext(state)
  provide(applicationDetailContextKey, context)
  return context
}

export function useApplicationDetailContext() {
  const context = inject(applicationDetailContextKey)
  if (!context) throw new Error('Application detail context is unavailable')
  return context
}
