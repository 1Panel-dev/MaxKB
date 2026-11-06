import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import { renderToString } from '@vue/server-renderer'
import { setImmediate } from 'node:timers/promises'
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

function loadComponent(path, dependencies, inlineTemplate = false) {
  const { descriptor } = parse(readFileSync(new URL(`../src/${path}`, import.meta.url), 'utf8'))
  const script = compileScript(descriptor, { id: 'tool-workspace-dialog', inlineTemplate })
  const { outputText } = ts.transpileModule(script.content, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  return exports.default
}

function createToolDialog(t, resourceScope, workspaceId, toolTypes = ['CUSTOM', 'WORKFLOW', 'INTERNAL']) {
  const tools = [
    { id: 'tool-a', name: 'Tool A', workspace_id: 'workspace-a', is_active: true, tool_type: 'CUSTOM' },
    { id: 'skill-a', name: 'Skill A', workspace_id: 'workspace-a', is_active: true, tool_type: 'SKILL' },
    { id: 'tool-b', name: 'Tool B', workspace_id: 'workspace-b', is_active: true, tool_type: 'CUSTOM' },
    { id: 'skill-b', name: 'Skill B', workspace_id: 'workspace-b', is_active: true, tool_type: 'SKILL' },
    { id: 'disabled', name: 'Disabled', workspace_id: 'workspace-a', is_active: false, tool_type: 'CUSTOM' },
    { id: 'self', name: 'Self', workspace_id: 'workspace-a', is_active: true, tool_type: 'WORKFLOW' },
  ]
  const calls = []
  const emitted = []
  const api = (scope) => ({
    getAllTool: async (query) => {
      calls.push({ scope, query })
      return tools.filter(
        (tool) => (!query.workspace_id || tool.workspace_id === query.workspace_id) && (!query.name || tool.name.includes(query.name)),
      )
    },
  })
  const dependencies = {
    vue: { ...Vue, useTemplateRef: () => Vue.ref() },
    lodash,
    '@/components/global/mk-tooltip/constants': { TOOLTIP_SHOW_DELAY: 300 },
    '@/utils/resource-context': {
      isSystemResource: () => resourceScope === 'system-resource',
      isSystemSharedResource: () => resourceScope === 'system-shared',
      isWorkspaceResource: () => resourceScope === 'workspace',
    },
    '@/api/admin/workspace/tool/tool': api('workspace'),
    '@/api/admin/system/resource-management/tool/tool': api('system-resource'),
    '@/api/admin/system/shared-resources/tool/tool': api('system-shared'),
    '@/api/enums': { RESOURCE_TYPE: { TOOL: 'TOOL' }, TOOL_TYPE: { CUSTOM: 'CUSTOM', WORKFLOW: 'WORKFLOW', INTERNAL: 'INTERNAL' } },
    '@/constants/folder': { FOLDER_ENTRIES: { TOOL: { all: { id: 'all', name: '全部' } } } },
    '@/components/business/folder-tree/index.vue': {},
    '@/components/mk-card-checkbox/index.vue': {},
  }
  const component = loadComponent('components/business/select-tool-dialog/index.vue', dependencies)
  const props = Vue.reactive({ workspaceId, toolTypes, excludedIds: ['self'], title: '工具' })
  const scope = Vue.effectScope()
  const dialog = scope.run(() => component.setup(props, { expose() {}, emit: (...args) => emitted.push(args) }))
  t.after(() => scope.stop())
  return { dialog, props, calls, emitted }
}

test('公共工具和 Skills 弹窗按所属空间查询，搜索与刷新保留空间筛选', async (t) => {
  for (const toolTypes of [['CUSTOM', 'WORKFLOW', 'INTERNAL'], ['SKILL']]) {
    const { dialog, calls } = createToolDialog(t, 'system-resource', 'workspace-a', toolTypes)
    dialog.open([])
    await setImmediate()
    assert.deepEqual(calls[0], { scope: 'system-resource', query: { tool_type_list: toolTypes, workspace_id: 'workspace-a' } })
    assert.deepEqual(
      dialog.toolOptions.value.map(({ id }) => id),
      [toolTypes[0] === 'SKILL' ? 'skill-a' : 'tool-a'],
    )
    dialog.searchKeyword.value = ' A '
    await dialog.refreshTool()
    dialog.refreshResources()
    await setImmediate()
    assert.equal(calls.length, 3)
    for (const { query } of calls.slice(1)) {
      assert.deepEqual(query, { tool_type_list: toolTypes, workspace_id: 'workspace-a', name: 'A' })
    }
    assert.equal(dialog.loading.value, false)
  }
})

test('公共弹窗等待资源所属空间，打开期间详情加载后自动刷新', async (t) => {
  const { dialog, props, calls } = createToolDialog(t, 'system-resource', undefined)
  dialog.open([{ id: 'saved-tool' }])
  await setImmediate()
  assert.equal(calls.length, 0)
  assert.deepEqual(dialog.toolOptions.value, [])
  props.workspaceId = 'workspace-a'
  await setImmediate()
  assert.equal(calls.length, 1)
  assert.equal(calls[0].query.workspace_id, 'workspace-a')
  assert.deepEqual(dialog.selectedTool.value, [{ id: 'saved-tool' }])
  dialog.visible.value = false
  props.workspaceId = 'workspace-b'
  await setImmediate()
  assert.equal(calls.length, 1)
  dialog.open([])
  await setImmediate()
  assert.equal(calls[1].query.workspace_id, 'workspace-b')
  assert.deepEqual(
    dialog.toolOptions.value.map(({ id }) => id),
    ['tool-b'],
  )
})

test('公共弹窗保持工作空间目录查询及系统共享查询原有范围', async (t) => {
  for (const scope of ['workspace', 'system-shared']) {
    const { dialog, calls } = createToolDialog(t, scope, undefined)
    dialog.open([])
    await setImmediate()
    assert.deepEqual(calls, [
      { scope, query: { tool_type_list: ['CUSTOM', 'WORKFLOW', 'INTERNAL'], ...(scope === 'workspace' ? { folder_id: 'all' } : {}) } },
    ])
  }
})

test('工具选择不删除已有快照，取消不提交，确认返回独立副本', async (t) => {
  const { dialog, emitted } = createToolDialog(t, 'system-resource', 'workspace-a')
  const selected = [{ id: 'legacy-tool', name: '旧配置' }]
  dialog.open(selected)
  await setImmediate()
  dialog.toggleTool(dialog.toolOptions.value[0])
  dialog.visible.value = false
  dialog.resetData()
  assert.deepEqual(emitted, [])
  assert.deepEqual(selected, [{ id: 'legacy-tool', name: '旧配置' }])
  dialog.open(selected)
  await setImmediate()
  dialog.toggleTool(dialog.toolOptions.value[0])
  dialog.submit()
  assert.deepEqual(
    emitted[0][1].map(({ id }) => id),
    ['legacy-tool', 'tool-a'],
  )
  dialog.resetData()
  assert.equal(emitted[0][1].length, 2)
})

test('简易智能体与 AI 对话共用的资源设置将注入空间传给公共工具弹窗', async () => {
  const captured = []
  const SlotContainer = {
    setup:
      (_, { slots }) =>
      () =>
        slots.default?.(),
  }
  const dependencies = {
    vue: { ...Vue, resolveComponent: () => SlotContainer },
    'vue-router': { useRoute: () => ({ params: { toolId: 'current-tool' } }) },
    lodash,
    '@/utils/resource-context': { isSystemSharedResource: () => false },
    '@/api/enums': { TOOL_TYPE: { SKILL: 'SKILL' } },
    '@/components/business/select-tool-dialog/index.vue': {
      props: ['workspaceId', 'excludedIds'],
      setup: (props) => {
        captured.push({ workspaceId: props.workspaceId, excludedIds: props.excludedIds })
        return () => null
      },
    },
    '@/components/business/select-application-dialog/index.vue': { render: () => null },
    './McpSettingDialog.vue': { render: () => null },
  }
  const component = loadComponent('workflow-canvas/nodes/ai-chat-node/component/resource-setting/index.vue', dependencies, true)
  const app = Vue.createSSRApp(component, { setting: { tool_ids: [], skill_tool_ids: [], mcp_tool_ids: [], application_ids: [] } })
  app.provide('resourceWorkspaceId', Vue.ref('owner-workspace'))
  await renderToString(app)
  assert.deepEqual(captured, [{ workspaceId: 'owner-workspace', excludedIds: ['current-tool'] }])
})
