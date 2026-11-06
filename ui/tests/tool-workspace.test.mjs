import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import lodash from 'lodash'
import ts from 'typescript'
import * as Vue from 'vue'

function createStoreApi(getTools = async (query) => [{ id: `${query?.workspace_id ?? 'shared'}-tool` }]) {
  const filename = new URL('../src/workflow-canvas/store/index.ts', import.meta.url)
  const source = readFileSync(filename, 'utf8').replace(/import\.meta\.glob<\{ default: ApiModule \}>\([^\n]+\)/, 'testApiModules')
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const calls = []
  const testApiModules = Object.fromEntries(
    ['workspace', 'system-resource', 'system-shared'].map((scope) => [
      `./api/${scope}/index.ts`,
      {
        default: {
          getToolListWithShared: (query) => {
            calls.push({ scope, query })
            return getTools(query)
          },
        },
      },
    ]),
  )
  const exports = {}
  compileFunction(outputText, ['exports', 'testApiModules'])(exports, testApiModules)
  return { useWorkflowStore: exports.useWorkflowStore, calls }
}

test('系统资源工具查询使用资源所属空间，并隔离不同空间的缓存', async () => {
  const { useWorkflowStore, calls } = createStoreApi()
  const workspaceA = useWorkflowStore('system-resource', () => 'workspace-a')
  const workspaceB = useWorkflowStore('system-resource', () => 'workspace-b')
  const query = { tool_type_list: ['CUSTOM', 'WORKFLOW'] }
  const [toolsA, toolsB] = await Promise.all([workspaceA.getToolListWithShared(query), workspaceB.getToolListWithShared(query)])
  assert.deepEqual(toolsA, [{ id: 'workspace-a-tool' }])
  assert.deepEqual(toolsB, [{ id: 'workspace-b-tool' }])
  assert.deepEqual(await workspaceA.getToolListWithShared(query), toolsA)
  assert.equal(calls.length, 2)
  assert.deepEqual(
    calls.map(({ query }) => query.workspace_id),
    ['workspace-a', 'workspace-b'],
  )
  assert.deepEqual(query, { tool_type_list: ['CUSTOM', 'WORKFLOW'] })
  await workspaceA.force.getToolListWithShared(query)
  assert.equal(calls.length, 3)
  assert.equal(calls[2].query.workspace_id, 'workspace-a')
})

test('详情未加载时不发起跨空间查询，加载和切换后读取最新空间', async () => {
  const { useWorkflowStore, calls } = createStoreApi()
  let workspaceId
  const store = useWorkflowStore('system-resource', () => workspaceId)
  assert.deepEqual(await store.getToolListWithShared({ tool_type: 'MCP' }), [])
  assert.equal(calls.length, 0)
  workspaceId = 'workspace-a'
  await store.getToolListWithShared({ tool_type: 'MCP', workspace_id: 'workspace-b' })
  workspaceId = 'workspace-b'
  await store.getToolListWithShared({ tool_type: 'MCP' })
  assert.deepEqual(
    calls.map(({ query }) => query),
    [
      { tool_type: 'MCP', workspace_id: 'workspace-a' },
      { tool_type: 'MCP', workspace_id: 'workspace-b' },
    ],
  )
})

test('仅复用同一空间的在途工具查询', async () => {
  const resolveQueries = []
  const { useWorkflowStore, calls } = createStoreApi(() => new Promise((resolve) => resolveQueries.push(resolve)))
  const storeA = useWorkflowStore('system-resource', () => 'workspace-a')
  const storeB = useWorkflowStore('system-resource', () => 'workspace-b')
  const requestA = storeA.getToolListWithShared({ tool_type: 'DATA_SOURCE' })
  const requestA2 = storeA.force.getToolListWithShared({ tool_type: 'DATA_SOURCE' })
  const requestB = storeB.getToolListWithShared({ tool_type: 'DATA_SOURCE' })
  assert.equal(requestA, requestA2)
  assert.notEqual(requestA, requestB)
  assert.equal(calls.length, 2)
  resolveQueries.forEach((resolve, index) => resolve([{ id: `tool-${index}` }]))
  await Promise.all([requestA, requestA2, requestB])
})

test('工作空间与系统共享范围沿用原查询参数', async () => {
  const { useWorkflowStore, calls } = createStoreApi()
  for (const scope of ['workspace', 'system-shared']) {
    await useWorkflowStore(scope, () => 'resource-workspace').getToolListWithShared({ tool_type: 'SKILL' })
  }
  assert.deepEqual(calls, [
    { scope: 'workspace', query: { tool_type: 'SKILL' } },
    { scope: 'system-shared', query: { tool_type: 'SKILL' } },
  ])
})

test('工具菜单在资源详情加载后自动查询，并保留数据源与普通工具的类型筛选', async () => {
  const filename = new URL('../src/workflow-canvas/node-menu/ResourceNodeMenu.vue', import.meta.url)
  const { descriptor } = parse(readFileSync(filename, 'utf8'))
  const script = compileScript(descriptor, { id: 'tool-workspace-menu' })
  const { outputText } = ts.transpileModule(script.content, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  for (const dataSource of [false, true]) {
    const { useWorkflowStore, calls } = createStoreApi(async () => [])
    const workspaceId = Vue.ref()
    const mountedCallbacks = []
    const dependencies = {
      vue: {
        ...Vue,
        inject: (key) => (key === 'resourceScope' ? 'system-resource' : workspaceId),
        onMounted: (callback) => mountedCallbacks.push(callback),
      },
      'vue-router': { useRoute: () => ({ params: {} }) },
      lodash,
      '@/components/global/mk-tooltip/constants': { TOOLTIP_SHOW_DELAY: 300 },
      '@/api/admin/workspace/shared/tool': {},
      '@/api/admin/workspace/tool/tool': {},
      '@/api/enums': { RESOURCE_TYPE: { TOOL: 'TOOL' }, TOOL_TYPE: { CUSTOM: 'CUSTOM', WORKFLOW: 'WORKFLOW', DATA_SOURCE: 'DATA_SOURCE' } },
      '@/constants': { FOLDER_ENTRY_ID: { ALL: 'all', SHARED: 'shared' } },
      '@/utils/common': { isWorkFlow: () => true },
      '@/components/business/folder-tree/index.vue': {},
      '@/workflow-canvas/config/node-data': { applicationNode: {}, toolLibNode: {}, toolWorkflowLibNode: {} },
      '@/workflow-canvas/store': { useWorkflowStore },
      '@/workflow-canvas/types': { WorkflowKind: { DataSource: 'data-source' } },
    }
    const exports = {}
    compileFunction(outputText, ['require', 'exports'])((id) => {
      assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
      return dependencies[id]
    }, exports)
    const scope = Vue.effectScope()
    scope.run(() => exports.default.setup({ source: 'TOOL', dataSource }, { expose() {}, emit() {} }))
    mountedCallbacks.forEach((callback) => callback())
    assert.equal(calls.length, 0)
    workspaceId.value = 'owner-workspace'
    await Vue.nextTick()
    assert.deepEqual(calls, [
      {
        scope: 'system-resource',
        query: { ...(dataSource ? { tool_type: 'DATA_SOURCE' } : { tool_type_list: ['CUSTOM', 'WORKFLOW'] }), workspace_id: 'owner-workspace' },
      },
    ])
    scope.stop()
  }
})
