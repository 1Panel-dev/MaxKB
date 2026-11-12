import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'

function createDrawer(path, mode) {
  const source = readFileSync(new URL(`../src/views/knowledge-detail/library/${path}`, import.meta.url), 'utf8')
  const script = compileScript(parse(source).descriptor, { id: 'knowledge-upload-limit' })
  const { outputText } = ts.transpileModule(script.content, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    if (id === 'vue') return { ...Vue, provide() {}, useTemplateRef: () => Vue.ref() }
    if (id === './constants') return { DOCUMENT_UPLOAD_OPTIONS: {} }
    if (id === '@/components/mk-drag-upload/validation') return { getUploadValidationMessage() {} }
    if (id.endsWith('.vue') || id.startsWith('@/api/') || id.startsWith('@/constants/') || id === '@/utils/message') return {}
    assert.fail(`Unexpected dependency: ${id}`)
  }, exports)
  const props = Vue.reactive({ api: {}, knowledgeId: 'knowledge-a', mode, fileCountLimit: undefined })
  return { props, drawer: exports.default.setup(props, { expose() {}, emit() {} }) }
}

for (const [name, path, mode] of [
  ['文本', 'document/upload-document/UploadDocumentDrawer.vue', 'text'],
  ['表格', 'document/upload-document/UploadDocumentDrawer.vue', 'table'],
  ['QA', 'document/upload-document/UploadDocumentDrawer.vue', 'qa'],
  ['图片', 'image/upload-image/UploadImageDrawer.vue', undefined],
]) {
  test(`${name}上传采用知识库文件数量配置，并响应配置变化`, () => {
    const { props, drawer } = createDrawer(path, mode)
    assert.equal(drawer.countLimit.value, 50)
    for (const limit of [1, 20, 51, 100, 1000]) {
      props.fileCountLimit = limit
      assert.equal(drawer.countLimit.value, limit)
    }
    props.fileCountLimit = undefined
    assert.equal(drawer.countLimit.value, 50)
  })
}
