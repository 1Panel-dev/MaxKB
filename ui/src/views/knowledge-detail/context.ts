/** 知识库详情的资源范围、API 装配与详情数据共享。 */
import { computed, inject, provide, reactive, type ComputedRef, type InjectionKey } from 'vue'
import { useRoute } from 'vue-router'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedKnowledgeApi from '@/api/admin/workspace/shared/knowledge/knowledge'
import SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import SyncApi from '@/api/admin/workspace/knowledge/sync'
import type { KnowledgeDetail } from '@/api/types'
import type { ResourceScope } from '@/router/admin/types'

interface KnowledgeResourceApi {
  readonly knowledge: typeof KnowledgeApi | typeof SharedKnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi
  readonly sync?: typeof SyncApi
}

interface KnowledgeResourceConfig {
  resourceApi: KnowledgeResourceApi
  listRouteName: string
}

/** 仅配置真实存在的完整 API 对象；缺失模块不回退到 Workspace。 */
const resourceConfigs = {
  workspace: {
    resourceApi: { knowledge: KnowledgeApi, sync: SyncApi },
    listRouteName: 'workspace-knowledge-list',
  },
  'workspace-shared': {
    resourceApi: { knowledge: SharedKnowledgeApi },
    listRouteName: 'workspace-knowledge-list',
  },
  'system-resource': {
    resourceApi: { knowledge: SystemResourceKnowledgeApi },
    listRouteName: 'system-resource-knowledge',
  },
  'system-shared': {
    resourceApi: { knowledge: SystemSharedKnowledgeApi },
    listRouteName: 'system-shared-knowledge',
  },
} satisfies Record<ResourceScope, KnowledgeResourceConfig>

interface KnowledgeDetailState {
  knowledge: ComputedRef<KnowledgeDetail | undefined>
  replaceKnowledgeDetail: (knowledge: KnowledgeDetail) => void
}

interface KnowledgeDetailContext extends KnowledgeDetailState {
  knowledgeId: ComputedRef<string>
  resourceScope: ComputedRef<ResourceScope | undefined>
  resourceApi: KnowledgeResourceApi
  listRouteName: ComputedRef<string>
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
    get knowledge() {
      return resourceConfig.value.resourceApi.knowledge
    },
    get sync() {
      return resourceConfig.value.resourceApi.sync
    },
  })
  return {
    ...state,
    knowledgeId: computed(() => String(route.params.knowledgeId ?? '')),
    resourceScope,
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

export function useKnowledgeDetailContext() {
  const context = inject(knowledgeDetailContextKey)
  if (!context) throw new Error('Knowledge detail context is unavailable')
  return context
}

/** 设置页只属于可管理范围，在上下文边界排除 Workspace 共享只读资源。 */
export function useKnowledgeSettingContext() {
  const context = useKnowledgeDetailContext()
  const resourceApi = reactive({
    get knowledge() {
      const scope = context.resourceScope.value
      if (!scope || scope === 'workspace-shared') throw new Error('Knowledge settings require a managed resource scope')
      return resourceConfigs[scope].resourceApi.knowledge
    },
  })
  return { ...context, resourceApi }
}
