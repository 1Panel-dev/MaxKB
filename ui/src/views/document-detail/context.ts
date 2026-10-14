/** 文档分段页的资源 API 配置与返回导航。 */
import { computed, inject, provide, reactive, type InjectionKey } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import SharedDocumentApi from '@/api/admin/workspace/shared/knowledge/document'
import SystemResourceDocumentApi from '@/api/admin/system/resource-management/knowledge/document'
import SystemSharedDocumentApi from '@/api/admin/system/shared-resources/knowledge/document'
import ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import SharedParagraphApi from '@/api/admin/workspace/shared/knowledge/paragraph'
import SystemResourceParagraphApi from '@/api/admin/system/resource-management/knowledge/paragraph'
import SystemSharedParagraphApi from '@/api/admin/system/shared-resources/knowledge/paragraph'
import type { ResourceScope } from '@/router/admin/types'

const resourceConfigs = {
  workspace: { document: DocumentApi, paragraph: ParagraphApi },
  'workspace-shared': { document: SharedDocumentApi, paragraph: SharedParagraphApi },
  'system-resource': { document: SystemResourceDocumentApi, paragraph: SystemResourceParagraphApi },
  'system-shared': { document: SystemSharedDocumentApi, paragraph: SystemSharedParagraphApi },
} satisfies Record<ResourceScope, { document: typeof SharedDocumentApi; paragraph: typeof SharedParagraphApi }>

/** 共有查询方法保持必填，仅部分范围提供的方法标记为可选。 */
type ApiKeys<Api> = Api extends unknown ? keyof Api : never
type OptionalApiMethods<Api> = Pick<Api, keyof Api> & {
  [Method in Exclude<ApiKeys<Api>, keyof Api>]?: Api extends unknown ? (Method extends keyof Api ? Api[Method] : never) : never
}

export type DocumentParagraphApi = OptionalApiMethods<(typeof resourceConfigs)[ResourceScope]['paragraph']>

function createDocumentDetailContext() {
  const route = useRoute()
  const router = useRouter()
  const resourceConfig = computed(() => {
    const scope = route.meta.resourceScope
    if (!scope) throw new Error('Document detail resource scope is unavailable')
    return resourceConfigs[scope]
  })
  const resourceApi = reactive({
    get document(): OptionalApiMethods<(typeof resourceConfigs)[ResourceScope]['document']> {
      return resourceConfig.value.document
    },
    get paragraph(): DocumentParagraphApi {
      return resourceConfig.value.paragraph
    },
  })

  function handleBack() {
    const scope = route.meta.resourceScope
    if (!scope) throw new Error('Document detail resource scope is unavailable')
    void router.push({
      name: `${scope}-knowledge-document-list`,
      params: {
        ...(scope === 'workspace' || scope === 'workspace-shared' ? { workspaceId: route.params.workspaceId } : {}),
        knowledgeId: String(route.params.knowledgeId ?? ''),
        type: route.params.type,
      },
      query: route.query,
    })
  }

  return { resourceApi, handleBack }
}

const documentDetailContextKey: InjectionKey<ReturnType<typeof createDocumentDetailContext>> = Symbol('document-detail-context')

export function provideDocumentDetailContext() {
  const context = createDocumentDetailContext()
  provide(documentDetailContextKey, context)
  return context
}

export function useDocumentDetailContext() {
  return inject(documentDetailContextKey, createDocumentDetailContext, true)
}
