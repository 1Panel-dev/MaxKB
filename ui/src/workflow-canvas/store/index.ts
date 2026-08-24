import type { ModelItem, ModelProviderItem, RequestParams } from '@/api/types'

type ApiModule = {
  getModelList: (query?: RequestParams) => Promise<ModelItem[]>
  getProviderList: () => Promise<ModelProviderItem[]>
}

const apiModules = import.meta.glob<{ default: ApiModule }>('./api/*/index.ts', {
  eager: true,
})

const apiMap = Object.fromEntries(
  Object.entries(apiModules).map(([path, mod]) => {
    const key = path.match(/\.\/api\/(.+)\/index\.ts/)?.[1] ?? ''
    return [key, mod.default]
  }),
) as Record<string, ApiModule>

const cacheMap = new Map<string, Map<string, unknown>>()
const pendingMap = new Map<string, Map<string, Promise<unknown>>>()

export function useWorkflowStore(apiType: string): ApiModule {
  const api = apiMap[apiType]
  if (!api) {
    throw new Error(`[useWorkflowStore] unknown apiType: "${apiType}"`)
  }

  const cache = cacheMap.get(apiType) ?? new Map<string, unknown>()
  cacheMap.set(apiType, cache)

  const pending = pendingMap.get(apiType) ?? new Map<string, Promise<unknown>>()
  pendingMap.set(apiType, pending)

  return {
    getModelList(query?: RequestParams): Promise<ModelItem[]> {
      const key = `model:${JSON.stringify(query ?? {})}`
      if (cache.has(key)) return Promise.resolve(cache.get(key) as ModelItem[])
      if (pending.has(key)) return pending.get(key) as Promise<ModelItem[]>

      const promise = api.getModelList(query).then((list) => {
        cache.set(key, list)
        pending.delete(key)
        return list
      })

      pending.set(key, promise)
      return promise
    },
    getProviderList(): Promise<ModelProviderItem[]> {
      const key = 'provider'
      if (cache.has(key)) return Promise.resolve(cache.get(key) as ModelProviderItem[])
      if (pending.has(key)) return pending.get(key) as Promise<ModelProviderItem[]>

      const promise = api.getProviderList().then((list) => {
        cache.set(key, list)
        pending.delete(key)
        return list
      })

      pending.set(key, promise)
      return promise
    },
  }
}
