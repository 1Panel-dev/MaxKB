import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'

const dialogPaths = {
  improve: 'conversation-panel/components/log-message-footer/improve/ImproveDialog.vue',
  add: 'views/application-detail/chat-log/add-knowledge/AddKnowledgeDialog.vue',
}

function createDialog(kind, scope, applicationId, failQuery = false) {
  const filename = new URL(`../src/${dialogPaths[kind]}`, import.meta.url)
  const { descriptor } = parse(readFileSync(filename, 'utf8'))
  const script = compileScript(descriptor, { id: `chat-log-${kind}` })
  const { outputText } = ts.transpileModule(script.content, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const calls = []
  const mounted = []
  const knowledge = { id: 'knowledge', name: 'Knowledge' }
  const document = { id: 'document', name: 'Document' }
  const knowledgeApi = (apiScope) => ({
    getAllKnowledge: async (query) => {
      calls.push({ resource: 'knowledge', scope: apiScope, query })
      if (failQuery) throw new Error('Knowledge query failed')
      return [knowledge]
    },
  })
  const documentApi = (apiScope) => ({
    getAllDocuments: async (knowledgeId) => {
      calls.push({ resource: 'document', scope: apiScope, knowledgeId })
      return [document]
    },
  })
  const dependencies = {
    vue: {
      ...Vue,
      onMounted: (callback) => mounted.push(callback),
      useTemplateRef: () => Vue.ref({ clearValidate() {}, validate: async () => true }),
    },
    '@/api/admin/workspace/knowledge/knowledge': knowledgeApi('workspace'),
    '@/api/admin/system/resource-management/knowledge/knowledge': knowledgeApi('system-resource'),
    '@/api/admin/workspace/knowledge/document': documentApi('workspace'),
    '@/api/admin/system/resource-management/knowledge/document': documentApi('system-resource'),
    '@/utils/resource-context': { isSystemResource: () => scope === 'system-resource' },
    '@/utils/message': { MsgSuccess() {} },
    '@/utils/icon': { getFileIconUrl: () => '' },
  }
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  const api = {
    putChatRecordLog: async (...args) => calls.push({ resource: 'improve', args }),
    postChatLogAddKnowledge: async (...args) => calls.push({ resource: 'add', args }),
  }
  const dialog = exports.default.setup(
    { api, applicationId, chatId: 'chat', recordId: 'record', question: 'Question', answer: 'Answer' },
    { expose() {}, emit() {} },
  )
  const open = () => (kind === 'improve' ? mounted[0]() : dialog.open(['chat']))
  return { dialog, calls, open, knowledge, document }
}

for (const kind of Object.keys(dialogPaths)) {
  test(`${kind}: system knowledge query uses the current application`, async () => {
    for (const applicationId of ['application-a', 'application-b']) {
      const { dialog, calls, open, knowledge } = createDialog(kind, 'system-resource', applicationId)
      await open()
      assert.deepEqual(calls, [{ resource: 'knowledge', scope: 'system-resource', query: { application_id: applicationId } }])
      assert.deepEqual(dialog.knowledgeOptions.value, [knowledge])
      assert.equal(dialog.optionLoading.value, false)
    }
  })

  test(`${kind}: workspace knowledge query retains its existing scope`, async () => {
    const { calls, open } = createDialog(kind, 'workspace', 'application-a')
    await open()
    assert.deepEqual(calls, [{ resource: 'knowledge', scope: 'workspace', query: undefined }])
  })

  test(`${kind}: query failure clears loading without falling back to a global list`, async () => {
    const { dialog, calls, open } = createDialog(kind, 'system-resource', 'missing-application', true)
    await open()
    assert.equal(calls.length, 1)
    assert.equal(dialog.visible.value, true)
    assert.equal(dialog.optionLoading.value, false)
    assert.deepEqual(dialog.knowledgeOptions.value, [])
  })

  test(`${kind}: document selection and saving use the selected knowledge`, async () => {
    const { dialog, calls, open, document } = createDialog(kind, 'system-resource', 'application-a')
    await open()
    const form = kind === 'improve' ? dialog.improveForm : dialog.knowledgeForm
    form.knowledge_id = 'knowledge'
    form.document_id = 'previous-document'
    await dialog.handleKnowledgeChange('knowledge')
    assert.equal(form.document_id, '')
    assert.deepEqual(dialog.documentOptions.value, [document])
    assert.deepEqual(calls[1], { resource: 'document', scope: 'system-resource', knowledgeId: 'knowledge' })
    form.document_id = document.id
    await dialog.handleSubmit()
    assert.deepEqual(calls[2], {
      resource: kind,
      args:
        kind === 'improve'
          ? ['application-a', 'chat', 'record', 'knowledge', 'document', { title: '', content: 'Answer', problem_text: 'Question' }]
          : ['application-a', { knowledge_id: 'knowledge', document_id: 'document', chat_ids: ['chat'] }],
    })
    assert.equal(dialog.visible.value, false)
  })
}
