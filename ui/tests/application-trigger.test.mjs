import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'
import lodash from 'lodash'

function load(path, dependency) {
  let source = readFileSync(new URL(`../src/${path}`, import.meta.url), 'utf8')
  if (path.endsWith('.vue')) source = compileScript(parse(source).descriptor, { id: 'application-trigger' }).content
  const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])(dependency, exports)
  return exports.default
}

for (const [scope, prefix] of [
  ['system/resource-management', '/system/resource/application'],
  ['workspace', '/workspace/workspace-a/application'],
]) {
  test(`${scope} 新增资源触发器在当前范围加载智能体并保存任务参数`, async () => {
    const calls = []
    const application = { id: 'application-a', type: 'SIMPLE', user_input_field_list: [{ field: 'question' }] }
    function dependency(id) {
      if (id === 'vue') return Vue
      if (id === 'lodash') return lodash
      if (id === 'uuid') return { v7: () => 'generated-id' }
      if (id === '@/api/enums')
        return {
          RESOURCE_TYPE: { APPLICATION: 'APPLICATION', TOOL: 'TOOL' },
          TOOL_TYPE: {},
          TRIGGER_TYPE: { SCHEDULED: 'SCHEDULED' },
          SCHEDULE_TYPE: { DAILY: 'daily' },
        }
      if (id === '@/api/admin/core/request' || id === '../../core/request')
        return {
          get: async (url) => {
            calls.push(url)
            return application
          },
        }
      if (id === '@/utils/resource-context') return { getWorkspaceId: () => (scope === 'workspace' ? 'workspace-a' : undefined) }
      if (id === '@/utils/message') return { MsgSuccess() {} }
      if (id === '@/api/constants') return { ADMIN_API_BASE_PATH: '/admin/api' }
      if (id.endsWith('.vue') || id.startsWith('@/api/') || id.startsWith('@/constants/') || id.startsWith('@/utils/')) return {}
      assert.fail(`Unexpected dependency: ${id}`)
    }
    const applicationApi = load(`api/admin/${scope}/application/application.ts`, dependency)
    const component = load('views/trigger/trigger-form/TriggerFormDrawer.vue', dependency)
    const saved = []
    const resource = { source_type: 'APPLICATION', source_id: application.id, workspace_id: 'workspace-a' }
    const drawer = component.setup(
      { resource, applicationApi, resourceApi: { postResourceTrigger: async (...args) => saved.push(args) } },
      { expose() {}, emit() {} },
    )
    await drawer.open()
    assert.deepEqual(calls, [`${prefix}/application-a`])
    assert.deepEqual(drawer.resources.value['APPLICATION:application-a'], application)
    assert.equal(drawer.detailFailed.value, false)
    drawer.formRef.value = { validate: async () => true }
    drawer.taskExecutionRef.value = { validate: async () => true }
    drawer.form.value.name = 'Daily question'
    drawer.form.value.trigger_setting.schedule_type = 'daily'
    drawer.form.value.trigger_task[0].parameter = { question: 'hello' }
    await drawer.handleSave()
    assert.deepEqual(saved[0][0], resource)
    assert.deepEqual(saved[0][1].trigger_task, [{ source_type: 'APPLICATION', source_id: 'application-a', parameter: { question: 'hello' } }])
  })
}
