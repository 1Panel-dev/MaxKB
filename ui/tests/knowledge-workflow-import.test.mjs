import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import ts from 'typescript'
import { compileScript, parse } from '@vue/compiler-sfc'
import * as Vue from 'vue'
import lodash from 'lodash'

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
    return url.endsWith('/upload_document') ? { id: 'action-a' } : []
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

test('系统共享知识库点击导入后打开表单，并通过共享接口提交本地文档', async () => {
  const { context, requests } = createContext('system-shared')
  const workflow = { nodes: [{ id: 'source', type: 'data-source-local-node' }], edges: [] }
  const opened = []
  const emitted = []
  const refs = {
    workflowDrawerRef: Vue.ref({ open: (graph) => opened.push(graph) }),
    actionRef: Vue.ref({
      validate: async () => true,
      getData: () => ({ node_id: 'source', file_list: [{ file_id: 'file-a', status: 'success' }, { status: 'uploading' }] }),
    }),
  }
  function loadComponent(name) {
    const path = `views/knowledge-detail/library/document/import-document/${name}.vue`
    const { descriptor } = parse(readFileSync(new URL(`../src/${path}`, import.meta.url), 'utf8'))
    const script = compileScript(descriptor, { id: 'shared-workflow-import' })
    const { outputText } = ts.transpileModule(script.content, {
      compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
    })
    const exports = {}
    compileFunction(outputText, ['require', 'exports'])((id) => {
      if (id === 'vue') return { ...Vue, provide() {}, useTemplateRef: (key) => refs[key] ?? Vue.ref() }
      if (id === '@/constants/knowledge') return { KNOWLEDGE_TYPE_KEY: { WORKFLOW: 'workflow' } }
      if (id === '@/workflow-canvas/types') return { WorkflowNodeType: { DataSourceLocalNode: 'data-source-local-node' } }
      if (id === '@/utils/message') return { MsgWarning() {} }
      if (id.startsWith('@/api/') || id.endsWith('.vue')) return {}
      assert.fail(`Unexpected dependency: ${id}`)
    }, exports)
    return exports.default
  }
  const button = loadComponent('ButtonImportDocument').setup(
    { workflowApi: context.resourceApi.workflow, knowledgeType: 'workflow', knowledgeId: 'knowledge-a', workflow },
    { expose() {}, emit() {} },
  )
  await button.handleOpenImport()
  assert.equal(button.workflowDrawerMounted.value, true)
  assert.deepEqual(opened, [workflow])
  const drawer = loadComponent('WorkflowImportDocumentDrawer').setup(
    { api: context.resourceApi.workflow, knowledgeId: 'knowledge-a' },
    { expose() {}, emit: (...args) => emitted.push(args) },
  )
  drawer.open(opened[0])
  await drawer.handleSubmit()
  assert.deepEqual(requests, [
    {
      method: 'POST',
      url: '/system/shared/knowledge/knowledge-a/upload_document',
      payload: { data_source: { node_id: 'source', file_list: [{ file_id: 'file-a', status: 'success' }] }, knowledge_base: {} },
    },
  ])
  assert.equal(drawer.actionId.value, 'action-a')
  assert.equal(drawer.active.value, 'result')
  assert.deepEqual(emitted, [['refresh']])
})

function createDatasourceTree(scope, overrideLoader) {
  const { context, route, requests } = createContext(scope)
  const provided = new Map()
  function setup(path, props) {
    const { descriptor } = parse(readFileSync(new URL(`../src/${path}.vue`, import.meta.url), 'utf8'))
    const script = compileScript(descriptor, { id: 'datasource-tree' })
    const { outputText } = ts.transpileModule(script.content, {
      compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
    })
    const exports = {}
    compileFunction(outputText, ['require', 'exports'])((id) => {
      if (id === 'vue')
        return {
          ...Vue,
          provide: (key, value) => provided.set(key, value),
          inject: (key) => provided.get(key),
          watch() {},
          useModel: () => Vue.ref(false),
          useAttrs: () => ({}),
          useTemplateRef: () => Vue.ref(),
        }
      if (id === 'lodash') return lodash
      if (id === 'element-plus') return { formItemContextKey: Symbol() }
      if (id === '@/api/admin/core/request')
        return {
          post: async (url, payload) => {
            requests.push({ method: 'POST', url, payload })
            return []
          },
        }
      if (id === '@/utils/resource-context') return { getWorkspaceId: () => route.params.workspaceId }
      if (id === '@/api/admin/workspace/knowledge/workflow') return { default: context.resourceApi.workflow }
      if (id === '@/workflow-canvas/types')
        return {
          WorkflowKind: { DataSource: 'data-source' },
          WorkflowNodeType: { DataSourceLocalNode: 'data-source-local-node', DataSourceWebNode: 'data-source-web-node' },
        }
      if (id === '@/components/mk-dynamics-form' || id === '@/utils/icon' || id === '@/workflow-canvas/icons/utils') return {}
      assert.fail(`Unexpected dependency: ${id}`)
    }, exports)
    return exports.default.setup(props, { expose() {}, emit() {} })
  }
  const workflow = { nodes: [{ id: 'source', type: 'tool-lib-node', properties: { kind: 'data-source', node_data: { tool_lib_id: 'tool-a' } } }] }
  const datasource = setup('views/workflow/knowledge/debug/action/DataSource', {
    api: context.resourceApi.workflow,
    knowledgeId: 'knowledge-a',
    workflow,
  })
  if (overrideLoader) provided.set('loadTreeData', overrideLoader)
  if (overrideLoader === null) provided.delete('loadTreeData')
  const tree = setup('components/mk-dynamics-form/items/tree/Tree', {
    modelValue: [],
    formField: { attrs: { lazy: true, fetch_list_function: 'get_file_list' } },
    otherParams: { current_knowledge_id: 'knowledge-a', current_workspace_id: route.params.workspaceId },
  })
  return { datasource, tree, requests, route, provided }
}

for (const [scope, prefix] of [
  ['workspace', '/workspace/workspace-a/knowledge'],
  ['system-resource', '/system/resource/knowledge'],
  ['system-shared', '/system/shared/knowledge'],
]) {
  test(`${scope} 数据源表单及目录树根、子节点使用相同接口范围`, async () => {
    const { datasource, tree, requests } = createDatasourceTree(scope)
    await datasource.handleSourceChange('source')
    await tree.loadDocuments()
    const folder = { token: 'folder-a', type: 'folder', name: 'Documents' }
    await tree.loadDocuments(folder)
    assert.equal(requests[0].url, `${prefix}/knowledge-a/datasource/tool/tool-a/form_list`)
    assert.deepEqual(requests.slice(1), [
      { method: 'POST', url: `${prefix}/knowledge-a/datasource/tool/tool-a/get_file_list`, payload: { current_node: undefined } },
      { method: 'POST', url: `${prefix}/knowledge-a/datasource/tool/tool-a/get_file_list`, payload: { current_node: folder } },
    ])
    assert.equal(tree.pendingLoads.value, 0)
  })
}

test('共享数据源加载失败释放 loading，保留错误且不回退工作空间接口', async () => {
  const { datasource, tree, requests } = createDatasourceTree('system-shared', async () => {
    throw new Error('Denied')
  })
  await datasource.handleSourceChange('source')
  await assert.rejects(tree.loadDocuments(), /Denied/)
  assert.equal(tree.pendingLoads.value, 0)
  assert.equal(requests.length, 1)
})

test('切换到本地数据源后清除上一个工具上下文', async () => {
  const { datasource, provided, requests } = createDatasourceTree('system-shared')
  await datasource.handleSourceChange('source')
  datasource.sourceNodeList.value.push({ id: 'local', type: 'data-source-local-node', properties: {} })
  await datasource.handleSourceChange('local')
  const count = requests.length
  assert.deepEqual(await provided.get('loadTreeData')('get_file_list'), [])
  assert.equal(requests.length, count)
})

test('未注入查询方法的目录树保持原工作空间请求协议', async () => {
  const { datasource, tree, requests } = createDatasourceTree('workspace', null)
  await datasource.handleSourceChange('source')
  await tree.loadDocuments()
  assert.equal(requests[1].url, '/workspace/workspace-a/knowledge/knowledge-a/datasource/tool/tool-a/get_file_list')
})
