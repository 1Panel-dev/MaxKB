import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'

const filename = new URL('../src/views/knowledge-detail/problem/components/AssociateParagraphDialog.vue', import.meta.url)
const { descriptor } = parse(readFileSync(filename, 'utf8'))
const script = compileScript(descriptor, { id: 'problem-association-test' })
const { outputText } = ts.transpileModule(script.content, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
})

// 执行实际弹窗的 setup 和交互方法，仅替换页面上下文、请求与无 DOM 的模板引用。
function createDialog(initialParagraphs = [], { associate, unassociate } = {}) {
  const calls = []
  const events = []
  const messages = []
  const resourceApi = {
    document: { getAllDocuments: async () => [] },
    problem: {
      getProblemDetail: async (...args) => {
        calls.push(['detail', ...args])
        return initialParagraphs
      },
      putBatchAssociateProblems: async (...args) => {
        calls.push(['associate', ...args])
        await associate?.(...args)
      },
    },
    paragraph: {
      putUnassociateParagraphProblem: async (...args) => {
        calls.push(['unassociate', ...args])
        await unassociate?.(...args)
      },
    },
  }
  const dependencies = {
    vue: { ...Vue, useTemplateRef: () => Vue.ref() },
    '@/components/mk-search-list/index.vue': {},
    '@/api/enums': { DOCUMENT_RESOURCE_TYPE: { DOCUMENT: 'DOCUMENT', IMAGE: 'IMAGE' } },
    '@/constants/knowledge': { KNOWLEDGE_TYPE_KEY: {}, KNOWLEDGE_TYPE_MAP: {} },
    '@/utils/common': { getFileUrl: () => '' },
    '@/utils/icon': { getFileIconUrl: () => '' },
    '@/utils/message': { MsgSuccess: (message) => messages.push(message) },
    '@/views/knowledge-detail/context': {
      useKnowledgeDetailContext: () => ({ knowledgeId: Vue.ref('knowledge-a'), resourceApi }),
    },
  }
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  const dialog = exports.default.setup({}, { expose() {}, emit: (event) => events.push(event) })
  return { dialog, calls, events, messages }
}

const webParagraph = { id: 'paragraph-web', document_id: 'document-pdf' }
const textParagraph = { id: 'paragraph-text', document_id: 'document-text' }
const imageParagraph = { id: 'paragraph-image', document_id: 'document-image' }

test('取消唯一已关联分段后确认，提交解除关联并刷新列表', async () => {
  const { dialog, calls, events } = createDialog([webParagraph])
  await dialog.open(['problem-a'])
  dialog.handleToggleParagraph(webParagraph)
  assert.equal(dialog.selectedParagraphs.value.length, 0)
  await dialog.handleSubmit()
  assert.deepEqual(calls, [
    ['detail', 'knowledge-a', 'problem-a'],
    ['unassociate', 'knowledge-a', 'document-pdf', 'paragraph-web', 'problem-a'],
  ])
  assert.equal(dialog.visible.value, false)
  assert.deepEqual(events, ['success'])
})

test('同时新增和取消跨文档分段，只提交差异并保留未变更关联', async () => {
  const { dialog, calls } = createDialog([webParagraph, textParagraph])
  await dialog.open(['problem-a'])
  dialog.handleToggleParagraph(webParagraph)
  dialog.handleToggleParagraph(imageParagraph)
  await dialog.handleSubmit()
  assert.deepEqual(calls.slice(1), [
    [
      'associate',
      'knowledge-a',
      {
        problem_id_list: ['problem-a'],
        paragraph_list: [{ paragraph_id: 'paragraph-image', document_id: 'document-image' }],
      },
    ],
    ['unassociate', 'knowledge-a', 'document-pdf', 'paragraph-web', 'problem-a'],
  ])
})

test('恢复原勾选后确认不发写请求，取消关闭也不保存草稿', async () => {
  const { dialog, calls, events } = createDialog([webParagraph])
  await dialog.open(['problem-a'])
  dialog.handleToggleParagraph(webParagraph)
  dialog.handleToggleParagraph(webParagraph)
  await dialog.handleSubmit()
  assert.equal(dialog.visible.value, false)
  assert.equal(calls.length, 1)
  assert.deepEqual(events, [])
  dialog.handleClosed()
  await dialog.open(['problem-a'])
  dialog.handleToggleParagraph(webParagraph)
  dialog.visible.value = false
  dialog.handleClosed()
  await dialog.open(['problem-a'])
  assert.equal(dialog.isSelected(webParagraph.id), true)
  assert.ok(calls.every(([method]) => method === 'detail'))
})

test('批量问题继续只添加所选分段，不查询或解除各问题原有关联', async () => {
  const { dialog, calls } = createDialog([webParagraph])
  await dialog.open(['problem-a', 'problem-b'])
  dialog.handleToggleParagraph(imageParagraph)
  await dialog.handleSubmit()
  assert.deepEqual(calls, [
    [
      'associate',
      'knowledge-a',
      {
        problem_id_list: ['problem-a', 'problem-b'],
        paragraph_list: [{ paragraph_id: 'paragraph-image', document_id: 'document-image' }],
      },
    ],
  ])
})

test('解除失败保留选择，恢复提交状态并允许重试', async () => {
  let failing = true
  const { dialog, calls, events, messages } = createDialog([webParagraph], {
    unassociate: async () => {
      if (failing) throw new Error('Failed to unlink')
    },
  })
  await dialog.open(['problem-a'])
  dialog.handleToggleParagraph(webParagraph)
  await dialog.handleSubmit()
  assert.equal(dialog.visible.value, true)
  assert.equal(dialog.isSelected(webParagraph.id), false)
  assert.equal(dialog.operationLoading.value, false)
  assert.deepEqual(events, [])
  assert.deepEqual(messages, [])
  failing = false
  await dialog.handleSubmit()
  assert.equal(calls.filter(([method]) => method === 'unassociate').length, 2)
  assert.equal(dialog.visible.value, false)
  assert.deepEqual(events, ['success'])
})

test('部分成功后重试跳过已解除项，重新勾选已解除项时能补回关联', async () => {
  for (const reselect of [false, true]) {
    let failing = true
    const { dialog, calls } = createDialog([webParagraph, textParagraph], {
      unassociate: async (_knowledgeId, _documentId, paragraphId) => {
        if (paragraphId === textParagraph.id && failing) throw new Error('Failed to unlink')
      },
    })
    await dialog.open(['problem-a'])
    dialog.handleToggleParagraph(webParagraph)
    dialog.handleToggleParagraph(textParagraph)
    await dialog.handleSubmit()
    assert.equal(dialog.visible.value, true)
    failing = false
    if (reselect) dialog.handleToggleParagraph(webParagraph)
    const completedCalls = calls.length
    await dialog.handleSubmit()
    const expectedCalls = [['unassociate', 'knowledge-a', 'document-text', 'paragraph-text', 'problem-a']]
    if (reselect)
      expectedCalls.unshift([
        'associate',
        'knowledge-a',
        {
          problem_id_list: ['problem-a'],
          paragraph_list: [{ paragraph_id: 'paragraph-web', document_id: 'document-pdf' }],
        },
      ])
    assert.deepEqual(calls.slice(completedCalls), expectedCalls)
    assert.equal(dialog.visible.value, false)
  }
})

test('新增成功但解除失败后，可以取消刚新增的关联并再次提交', async () => {
  let failing = true
  const { dialog, calls } = createDialog([webParagraph], {
    unassociate: async () => {
      if (failing) throw new Error('Failed to unlink')
    },
  })
  await dialog.open(['problem-a'])
  dialog.handleToggleParagraph(webParagraph)
  dialog.handleToggleParagraph(imageParagraph)
  await dialog.handleSubmit()
  assert.equal(dialog.visible.value, true)
  failing = false
  dialog.handleToggleParagraph(imageParagraph)
  const completedCalls = calls.length
  await dialog.handleSubmit()
  assert.deepEqual(calls.slice(completedCalls), [
    ['unassociate', 'knowledge-a', 'document-pdf', 'paragraph-web', 'problem-a'],
    ['unassociate', 'knowledge-a', 'document-image', 'paragraph-image', 'problem-a'],
  ])
  assert.equal(dialog.visible.value, false)
})
