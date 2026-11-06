import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import ts from 'typescript'
import * as Vue from 'vue'

function loadModule(path, resolveDependency) {
  const { outputText } = ts.transpileModule(readFileSync(new URL(`../src/${path}.ts`, import.meta.url), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])(resolveDependency, exports)
  return exports
}

// 执行真实详情上下文与工作流 API，只替换路由和 HTTP 传输。
function createContext(scope) {
  const route = Vue.reactive({
    meta: { resourceScope: scope },
    params: { knowledgeId: 'knowledge-a', ...(scope === 'workspace' ? { workspaceId: 'workspace-a' } : {}) },
  })
  const requests = []
  const request = (method) => async (url, payload) => {
    requests.push({ method, url, payload })
    return []
  }
  const resourceContext = {
    getResourceScope: () => route.meta.resourceScope,
    getWorkspaceId: () => route.params.workspaceId,
    isWorkspaceResource: () => route.meta.resourceScope === 'workspace',
    isWorkspaceSharedResource: () => route.meta.resourceScope === 'workspace-shared',
  }
  function resolveDependency(id) {
    if (id === 'vue') return { ...Vue, provide() {} }
    if (id === 'vue-router') return { useRoute: () => route }
    if (id === '@/utils/resource-context') return resourceContext
    if (id === '@/utils/message') return { MsgWarning() {} }
    if (id === '@/api/admin/core/request' || id === '../../core/request') {
      return { get: request('GET'), post: request('POST'), put: request('PUT') }
    }
    if (id.startsWith('@/api/') && id.endsWith('/workflow')) return loadModule(id.slice(2), resolveDependency)
    if (id.startsWith('@/api/')) return {}
    assert.fail(`Unexpected dependency: ${id}`)
  }
  const { provideKnowledgeDetailContext } = loadModule('views/knowledge-detail/context', resolveDependency)
  const context = provideKnowledgeDetailContext({ knowledge: Vue.computed(() => undefined), replaceKnowledgeDetail() {} })
  return { context, route, requests }
}

for (const [scope, prefix] of [
  ['workspace', '/workspace/workspace-a/knowledge'],
  ['system-resource', '/system/resource/knowledge'],
  ['system-shared', '/system/shared/knowledge'],
]) {
  test(`${scope} 文档导入的表单、提交和结果查询使用同一资源范围`, async () => {
    const { context, requests } = createContext(scope)
    const api = context.resourceApi.workflow
    assert.ok(api, '可管理的知识库必须装配工作流 API')
    const node = { id: 'source', type: 'data-source-local-node' }
    const payload = { data_source: { node_id: node.id, file_list: [] }, knowledge_base: {} }
    await api.getKnowledgeWorkflowFormList('knowledge-a', 'local', node.type, node)
    await api.postKnowledgeWorkflowImport('knowledge-a', payload)
    await api.getKnowledgeWorkflowAction('knowledge-a', 'action-a')
    assert.deepEqual(requests, [
      { method: 'POST', url: `${prefix}/knowledge-a/datasource/local/${node.type}/form_list`, payload: { node } },
      { method: 'POST', url: `${prefix}/knowledge-a/upload_document`, payload },
      { method: 'GET', url: `${prefix}/knowledge-a/action/action-a`, payload: undefined },
    ])
  })
}

test('工作空间共享知识库保持只读，不装配文档导入 API', () => {
  assert.equal(createContext('workspace-shared').context.resourceApi.workflow, undefined)
})

test('详情资源范围切换后，表单请求使用新范围而不保留工作空间 API', async () => {
  const { context, route, requests } = createContext('workspace')
  const resourceApi = context.resourceApi
  route.meta.resourceScope = 'system-resource'
  delete route.params.workspaceId
  await resourceApi.workflow.getKnowledgeWorkflowFormList('knowledge-a', 'tool', 'tool-a', { id: 'source' })
  assert.equal(requests[0].url, '/system/resource/knowledge/knowledge-a/datasource/tool/tool-a/form_list')
})
