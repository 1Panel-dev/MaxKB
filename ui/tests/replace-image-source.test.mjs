import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'

function createAction(resourceType) {
  const { descriptor } = parse(
    readFileSync(new URL('../src/views/knowledge-detail/library/document/action-dropdown/ReplaceDocumentAction.vue', import.meta.url), 'utf8'),
  )
  const script = compileScript(descriptor, { id: 'replace-image-source' })
  const { outputText } = ts.transpileModule(script.content, { compilerOptions: { module: ts.ModuleKind.CommonJS } })
  const calls = [],
    warnings = []
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    if (id === 'vue') return { ...Vue, useModel: () => Vue.ref(false) }
    if (id === '@/utils/message') return { MsgSuccess() {}, MsgWarning: (text) => warnings.push(text) }
    if (id === '@/api/enums') return { DOCUMENT_RESOURCE_TYPE: { IMAGE: 'image', DOCUMENT: 'document' } }
    if (id === '@/constants/knowledge')
      return {
        KNOWLEDGE_IMAGE_EXTENSIONS: ['JPG', 'JPEG', 'PNG', 'WEBP', 'BMP'],
        KNOWLEDGE_IMAGE_ACCEPT: '.jpg,.jpeg,.png,.webp,.bmp',
        KNOWLEDGE_IMAGE_TYPE_LABEL: 'JPG、JPEG、PNG、WEBP、BMP',
      }
    assert.fail(`Unexpected dependency: ${id}`)
  }, exports)
  const action = exports.default.setup(
    {
      api: { postReplaceDocumentSource: async (...args) => calls.push(args) },
      knowledgeId: 'knowledge',
      document: { id: 'document', resource_type: resourceType },
    },
    { expose() {}, emit() {} },
  )
  return { action, calls, warnings }
}

test('图片替换过滤文件选择，并拒绝非图片文件提交', async () => {
  const { action, calls, warnings } = createAction('image')
  assert.equal(action.accept.value, '.jpg,.jpeg,.png,.webp,.bmp')
  for (const name of ['document.pdf', 'file.docx', 'image.png.txt', 'image.gif']) await action.handleReplace({ raw: { name } })
  assert.equal(calls.length, 0)
  assert.equal(warnings.length, 4)
  assert.equal(action.loading.value, false)
})

test('支持的图片扩展名不区分大小写', async () => {
  const { action, calls } = createAction('image')
  for (const name of ['image.JPG', 'image.jpeg', 'image.png', 'image.webp', 'image.bmp']) await action.handleReplace({ raw: { name } })
  assert.equal(calls.length, 5)
})

test('普通文档替换保留原有文件选择范围', async () => {
  const { action, calls } = createAction('document')
  assert.equal(action.accept.value, '')
  await action.handleReplace({ raw: { name: 'document.pdf' } })
  assert.equal(calls.length, 1)
})
