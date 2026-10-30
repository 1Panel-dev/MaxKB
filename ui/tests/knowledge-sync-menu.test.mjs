import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileTemplate, parse } from '@vue/compiler-sfc'
import { renderToString } from '@vue/server-renderer'
import ts from 'typescript'
import * as Vue from 'vue'
import { KNOWLEDGE_TYPE } from '../src/api/enums/knowledge.ts'

function findSyncAction(node) {
  if (node.tag === 'SyncKnowledgeAction') return node
  for (const child of node.children ?? []) {
    const action = findSyncAction(child)
    if (action) return action
  }
}

// 编译各页面实际的同步入口，隔离列表加载与其他操作，验证菜单渲染结果。
for (const [scope, path] of [
  ['工作空间', 'knowledge/index.vue'],
  ['系统资源管理', 'system/resource-management/knowledge/index.vue'],
  ['系统共享资源', 'system/shared-resources/knowledge/index.vue'],
]) {
  const filename = new URL(`../src/views/${path}`, import.meta.url)
  const { descriptor } = parse(readFileSync(filename, 'utf8'))
  const action = findSyncAction(descriptor.template.ast)
  assert.ok(action, `${scope}缺少同步入口`)
  const { code, errors } = compileTemplate({ source: action.loc.source, filename: path, id: path })
  assert.deepEqual(errors, [])
  const { outputText } = ts.transpileModule(code, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.equal(id, 'vue')
    return Vue
  }, exports)

  for (const [label, type, visible] of [
    ['飞书', KNOWLEDGE_TYPE.LARK, false],
    ['Web', KNOWLEDGE_TYPE.WEB, true],
    ['通用', KNOWLEDGE_TYPE.BASE, false],
    ['工作流', KNOWLEDGE_TYPE.WORKFLOW, false],
  ]) {
    test(`${scope}的${label}知识库${visible ? '显示' : '隐藏'}整库同步菜单`, async () => {
      const app = Vue.createSSRApp({
        setup: () => ({
          KNOWLEDGE_TYPE,
          knowledge: { id: 'knowledge-a', type },
          row: { id: 'knowledge-a', type },
          knowledgeOperationLoading: false,
          KnowledgeApi: {},
          SystemResourceKnowledgeApi: {},
          SystemSharedKnowledgeApi: {},
        }),
        render: exports.render,
      })
      app.component('SyncKnowledgeAction', {
        inheritAttrs: false,
        props: ['label'],
        setup: (props) => () => Vue.h('button', props.label),
      })
      const html = await renderToString(app)
      assert.equal(html.includes('<button>同步</button>'), visible)
    })
  }
}
