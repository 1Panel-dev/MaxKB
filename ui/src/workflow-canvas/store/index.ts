import type { Dict, DynamicFormField, ModelItem, ModelProviderItem, ToolItem } from '@/api/types'

export interface McpTool {
  args_schema: Record<string, unknown>
  description: string
  name: string
  server: string
}

// 底层 api/*/index.ts 提供的原始接口实现,不含缓存层能力。
type ApiModule = {
  getModelList: (query?: Dict<unknown>) => Promise<ModelItem[]>
  getProviderList: () => Promise<ModelProviderItem[]>
  getModelParamsForm: (modelId: string) => Promise<DynamicFormField[]>
  getMcpTools?: (resourceType: string, resourceId: string, mcpServers: string) => Promise<McpTool[]>
  getAllToolList?: (query?: Dict<unknown>) => Promise<ToolItem[]>
  getToolById?: (toolId: string) => Promise<ToolItem>
}

// useWorkflowStore 返回的包装接口:默认走缓存,通过 store.force.xxx() 强制刷新。
export type WorkflowStoreApi = {
  getModelList: (query?: Dict<unknown>) => Promise<ModelItem[]>
  getProviderList: () => Promise<ModelProviderItem[]>
  getModelParamsForm: (modelId: string) => Promise<DynamicFormField[]>
  getMcpTools: (resourceType: string, resourceId: string, mcpServers: string) => Promise<McpTool[]>
  getAllToolList: (query?: Dict<unknown>) => Promise<ToolItem[]>
  getToolById: (toolId: string) => Promise<ToolItem>
}

type WorkflowStore = WorkflowStoreApi & { force: WorkflowStoreApi }

const apiModules = import.meta.glob<{ default: ApiModule }>('./api/*/index.ts', { eager: true })

const apiMap = Object.fromEntries(
  Object.entries(apiModules).map(([path, mod]) => {
    const key = path.match(/\.\/api\/(.+)\/index\.ts/)?.[1] ?? ''
    return [key, mod.default]
  }),
) as Record<string, ApiModule>

const cacheMap = new Map<string, Map<string, unknown>>()
const pendingMap = new Map<string, Map<string, Promise<unknown>>>()

export function useWorkflowStore(apiType: string): WorkflowStore {
  const api: ApiModule | undefined = apiMap[apiType]
  if (!api) {
    throw new Error(`[useWorkflowStore] unknown apiType: "${apiType}"`)
  }
  const resolvedApi: ApiModule = api

  const cache = cacheMap.get(apiType) ?? new Map<string, unknown>()
  cacheMap.set(apiType, cache)

  const pending = pendingMap.get(apiType) ?? new Map<string, Promise<unknown>>()
  pendingMap.set(apiType, pending)

  // 统一的缓存 + 请求去重逻辑。force 时跳过缓存读取并覆盖缓存,但仍复用在途请求以避免重复触发。
  function withCache<T>(key: string, fetcher: () => Promise<T>, force = false): Promise<T> {
    if (!force && cache.has(key)) return Promise.resolve(cache.get(key) as T)
    if (pending.has(key)) return pending.get(key) as Promise<T>

    const promise = fetcher().then((data) => {
      cache.set(key, data)
      pending.delete(key)
      return data
    })

    pending.set(key, promise)
    return promise
  }

  // 生成一组接口方法;force 为 true 时对应的调用会跳过缓存强制刷新。
  function build(force: boolean): WorkflowStoreApi {
    return {
      getModelList(query?: Dict<unknown>): Promise<ModelItem[]> {
        return withCache(`model:${JSON.stringify(query ?? {})}`, () => resolvedApi.getModelList(query), force)
      },
      getProviderList(): Promise<ModelProviderItem[]> {
        return withCache('provider', () => resolvedApi.getProviderList(), force)
      },
      getModelParamsForm(modelId: string): Promise<DynamicFormField[]> {
        return withCache(`modelParamsForm:${modelId}`, () => resolvedApi.getModelParamsForm(modelId), force)
      },
      getMcpTools(resourceType: string, resourceId: string, mcpServers: string): Promise<McpTool[]> {
        if (!resolvedApi.getMcpTools) return Promise.resolve([])
        return withCache(`mcp-tools:${resourceType}:${resourceId}:${mcpServers}`, () => resolvedApi.getMcpTools!(resourceType, resourceId, mcpServers), force)
      },
      getAllToolList(query?: Dict<unknown>): Promise<ToolItem[]> {
        if (!resolvedApi.getAllToolList) return Promise.resolve([])
        return withCache(`tool-list:${JSON.stringify(query ?? {})}`, () => resolvedApi.getAllToolList!(query), force)
      },
      getToolById(toolId: string): Promise<ToolItem> {
        if (!resolvedApi.getToolById) return Promise.resolve({} as ToolItem)
        return withCache(`tool:${toolId}`, () => resolvedApi.getToolById!(toolId), force)
      },
    }
  }

  return { ...build(false), force: build(true) }
}
