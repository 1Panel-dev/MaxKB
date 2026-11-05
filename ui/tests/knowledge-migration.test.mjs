import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { setImmediate } from 'node:timers/promises'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'

const source = { id: 'source-knowledge', workspace_id: 'workspace-a' }
const target = { id: 'target-knowledge', workspace_id: 'workspace-a' }
const dialogPaths = {
  document: 'knowledge-detail/library/document/action-dropdown/migrate/DocumentMigrateDialog.vue',
  paragraph: 'document-detail/action-dropdown/migrate/ParagraphMigrateDialog.vue',
}

function createDialog(kind, scope, getKnowledge = async () => [source, target]) {
  const filename = new URL(`../src/views/${dialogPaths[kind]}`, import.meta.url)
  const { descriptor } = parse(readFileSync(filename, 'utf8'))
  const script = compileScript(descriptor, { id: `migration-${kind}` })
  const { outputText } = ts.transpileModule(script.content, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const calls = []
  const knowledgeApis = Object.fromEntries(
    ['workspace', 'system-resource', 'system-shared'].map((apiScope) => [
      apiScope,
      {
        getAllKnowledge: async (query) => {
          calls.push([apiScope, query])
          return getKnowledge()
        },
      },
    ]),
  )
  const resourceApi = {
    knowledge: knowledgeApis[scope],
    document: { getAllDocuments: async () => [{ id: 'source-document' }, { id: 'target-document' }] },
  }
  const dependencies = {
    vue: { ...Vue, useTemplateRef: () => Vue.ref(), useModel: () => Vue.ref(false) },
    '@/views/knowledge-detail/context': { useKnowledgeDetailContext: () => ({ resourceApi }) },
    '@/views/document-detail/context': { useDocumentDetailContext: () => ({ resourceApi }) },
    '@/api/admin/workspace/knowledge/knowledge': knowledgeApis.workspace,
    '@/api/admin/system/resource-management/knowledge/knowledge': knowledgeApis['system-resource'],
    '@/api/admin/system/shared-resources/knowledge/knowledge': knowledgeApis['system-shared'],
    '@/utils/resource-context': {
      isSystemResource: () => scope === 'system-resource',
      isSystemSharedResource: () => scope === 'system-shared',
    },
    '@/utils/message': { MsgSuccess() {} },
    '@/utils/icon': { getFileIconUrl: () => '' },
  }
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  const dialog = exports.default.setup({ api: {}, knowledgeId: source.id, documentId: 'source-document' }, { expose() {}, emit() {} })
  return { dialog, calls }
}

for (const kind of Object.keys(dialogPaths)) {
  for (const scope of ['workspace', 'system-resource', 'system-shared']) {
    test(`${scope} ${kind} migration queries with the source knowledge and preserves target exclusions`, async () => {
      const { dialog, calls } = createDialog(kind, scope)
      await dialog.open(['selected-resource'])
      await setImmediate()
      assert.deepEqual(calls, [[scope, { knowledge_id: source.id }]])
      assert.deepEqual(dialog.knowledgeOptions.value, kind === 'document' ? [target] : [source, target])
      assert.equal(dialog.optionLoading.value, false)
      if (kind === 'paragraph') {
        await dialog.handleKnowledgeChange(source.id)
        assert.deepEqual(dialog.documentOptions.value, [{ id: 'target-document' }])
      }
    })
  }

  test(`${kind} migration clears loading after a target query failure`, async () => {
    const { dialog } = createDialog(kind, 'system-resource', async () => {
      throw new Error('query failed')
    })
    await dialog.open(['selected-resource'])
    await setImmediate()
    assert.equal(dialog.optionLoading.value, false)
    assert.equal(dialog.visible.value, true)
    assert.deepEqual(dialog.knowledgeOptions.value, [])
  })
}
