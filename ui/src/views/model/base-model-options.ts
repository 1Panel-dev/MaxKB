import type { BaseModelOption } from '@/api/types'
import ProviderApi from '@/api/admin/model-provider'

function toCredentialRecord(credential?: Record<string, unknown>) {
  return credential && Object.keys(credential).length > 0 ? credential : undefined
}

/** 读取后端按 url+key 缓存的基础模型列表，未命中返回空数组；编辑时传 modelId 由后端用真实凭证取缓存。 */
export function loadCachedBaseModelOptions(
  provider: string,
  modelType: string,
  credential?: Record<string, unknown>,
  modelId?: string,
) {
  const credentialRecord = toCredentialRecord(credential)
  if (!credentialRecord && !modelId) return Promise.resolve<BaseModelOption[]>([])
  return ProviderApi.getBaseModelListCache(provider, modelType, credentialRecord ?? {}, modelId).catch(() => [])
}

/** 优先取后端缓存，未命中回落内置默认模型列表。 */
export function loadCachedOrBuiltinBaseModelOptions(
  provider: string,
  modelType: string,
  credential?: Record<string, unknown>,
  modelId?: string,
) {
  return loadCachedBaseModelOptions(provider, modelType, credential, modelId).then((options) => {
    if (options?.length) return options
    return ProviderApi.getBaseModelList(provider, modelType)
  })
}
