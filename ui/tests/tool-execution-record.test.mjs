import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { setImmediate } from 'node:timers/promises'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import { renderToString } from '@vue/server-renderer'
import ts from 'typescript'
import * as Vue from 'vue'

const sourceTypes = { APPLICATION: 'APPLICATION', KNOWLEDGE: 'KNOWLEDGE', TOOL: 'TOOL', TRIGGER: 'TRIGGER' }
const record = { id: 'weather-record', source_type: 'TOOL', source_name: 'get_city_weather', state: 'SUCCESS', create_time: '2026-11-06' }
const executionContent = { props: ['detail'], setup: (props) => () => Vue.h('section', { class: 'workflow-details' }, JSON.stringify(props.detail)) }

function loadDrawer(name, inlineTemplate = false) {
  const filename = new URL(`../src/views/workflow/tool/execution-record/${name}.vue`, import.meta.url)
  const { descriptor } = parse(readFileSync(filename, 'utf8'))
  const script = compileScript(descriptor, { id: name, inlineTemplate })
  const { outputText } = ts.transpileModule(script.content, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const dependencies = {
    vue: Vue,
    '@/api/enums': { TOOL_RECORD_SOURCE: sourceTypes, KNOWLEDGE_TYPE: { WORKFLOW: 4 }, STATE_TYPES: { SUCCESS: 'SUCCESS', STARTED: 'STARTED', FAILURE: 'FAILURE' } },
    '@/constants/state': { EXECUTION_STATUS_OPTIONS: { SUCCESS: { label: '成功' }, STARTED: { label: '执行中' }, FAILURE: { label: '失败' } } },
    '@/utils/time': { datetimeFormat: (value) => value },
    '@/utils/common': { toOrderBy: () => undefined },
    '@/utils/resource-context': { isSystemSharedResource: () => false },
    '@/workflow-canvas/execution-details/index.vue': executionContent,
    '@/workflow-canvas/types': { WorkflowMode: { Tool: 'tool' } },
    './ExecutionDetailDrawer.vue': {},
  }
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  return exports.default
}

test('嵌套工具显示工具类型，筛选时保留父工具来源名称', async () => {
  const queries = []
  const drawer = loadDrawer('ExecutionRecordDrawer').setup(
    { toolId: 'child-tool', api: { getToolExecutionRecordPage: async (...args) => {
      queries.push(args)
      return { records: [record], current: 1, size: 20, total: 1 }
    } } },
    { expose() {}, emit() {} },
  )
  drawer.open()
  await setImmediate()
  assert.equal(drawer.sourceLabels[drawer.recordData.value[0].source_type], '工具')
  assert.ok(drawer.sourceTypeOptions.some(({ label, value }) => label === '工具' && value === 'TOOL'))
  drawer.selectedSourceType.value = 'TOOL'
  drawer.searchRecords({ source_name: 'get_city_weather' })
  await setImmediate()
  assert.deepEqual(queries.at(-1), ['child-tool', { currentPage: 1, pageSize: 20 }, { source_name: 'get_city_weather', source_type: 'TOOL', order: undefined }])
})

async function renderDetail(meta) {
  const drawer = loadDrawer('ExecutionDetailDrawer', true)
  const calls = []
  const originalSetup = drawer.setup
  const app = Vue.createSSRApp({
    ...drawer,
    setup(props, context) {
      Vue.onServerPrefetch(setImmediate)
      return originalSetup(props, context)
    },
  }, {
    modelValue: true, toolId: 'child-tool', record, previousDisabled: true, nextDisabled: true,
    api: { getToolExecutionRecordDetail: async (...args) => {
      calls.push(args)
      return { id: record.id, state: 'SUCCESS', meta }
    } },
  })
  const container = { setup: (_, { slots }) => () => Vue.h('div', slots.default?.()) }
  for (const name of ['MkDrawer', 'ElCard', 'ElButton']) app.component(name, container)
  for (const name of ['MkIcon', 'KnowledgeIcon', 'TriggerIcon', 'ApplicationIcon', 'ToolIcon', 'MkStatusLabel']) {
    app.component(name, { setup: () => () => Vue.h('i', { 'data-icon': name }) })
  }
  app.directive('loading', {})
  const html = await renderToString(app)
  assert.deepEqual(calls, [['child-tool', record.id]])
  return html
}

test('代码工具执行详情显示父工具图标、输入和输出', async () => {
  const html = await renderDetail({ input: { city: 'Hangzhou' }, output: { weather: 'sunny' } })
  assert.match(html, /get_city_weather/)
  assert.match(html, /data-icon="ToolIcon"/)
  assert.match(html, /输入/)
  assert.match(html, /Hangzhou/)
  assert.match(html, /输出/)
  assert.match(html, /sunny/)
})

test('代码工具详情保留 false、零和执行错误', async () => {
  for (const output of [false, 0, 'Error: weather unavailable']) {
    const html = await renderDetail({ input: { enabled: false }, output })
    assert.match(html, /输入/)
    assert.ok(html.includes(String(output)))
  }
})

test('工作流工具继续使用节点详情，兼容数组和对象格式', async () => {
  const node = { node_id: 'weather', type: 'tool-lib-node', result: 'sunny' }
  for (const details of [[node], { weather: node }]) {
    const html = await renderDetail({ details, input: { ignored: 'unused-input' } })
    assert.match(html, /class="workflow-details"/)
    assert.match(html, /sunny/)
    assert.doesNotMatch(html, /unused-input/)
  }
})
