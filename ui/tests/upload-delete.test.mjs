import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'

function createUpload(deleteFile) {
  const { descriptor } = parse(readFileSync(new URL('../src/components/mk-drag-upload/MultipleFileUpload.vue', import.meta.url), 'utf8'))
  const script = compileScript(descriptor, { id: 'upload-delete' })
  const { outputText } = ts.transpileModule(script.content, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } })
  const files = Vue.ref([]),
    emitted = [],
    internalRemoved = []
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    if (id === 'vue')
      return {
        ...Vue,
        inject() {},
        watch() {},
        onBeforeUnmount() {},
        useModel: () => files,
        useTemplateRef: () => Vue.ref({ handleRemove: (file) => internalRemoved.push(file) }),
      }
    if (id === '@/api/admin/file') return { deleteFile }
    if (id === '@/utils/message') return { MsgWarning() {} }
    if (id.endsWith('.vue') || id.endsWith('.svg')) return {}
    assert.fail(`Unexpected dependency: ${id}`)
  }, exports)
  const component = exports.default.setup({ disabled: false, mode: 'image' }, { expose() {}, emit: (...args) => emitted.push(args) })
  files.value = [{ uid: 1, name: 'image.png', status: 'success', file_id: 'file-a' }]
  return { component, files, emitted, internalRemoved }
}

test('删除失败保留图片和控件内部列表，且不发出 remove 事件', async () => {
  const { component, files, emitted, internalRemoved } = createUpload(async () => {
    throw new Error('403')
  })
  await component.handleRemove(files.value[0])
  assert.equal(files.value.length, 1)
  assert.deepEqual(emitted, [])
  assert.deepEqual(internalRemoved, [])
})

test('等待服务端成功才移除图片，等待期间重复点击只提交一次', async () => {
  let resolveDelete,
    calls = 0
  const pending = new Promise((resolve) => {
    resolveDelete = resolve
  })
  const { component, files, emitted, internalRemoved } = createUpload(() => {
    calls++
    return pending
  })
  const file = files.value[0]
  const removing = component.handleRemove(file)
  await component.handleRemove(file)
  assert.equal(files.value.length, 1)
  assert.equal(calls, 1)
  resolveDelete()
  await removing
  assert.equal(files.value.length, 0)
  assert.equal(internalRemoved.length, 1)
  assert.deepEqual(emitted, [['remove', file]])
})

test('上传中文件取消请求并从列表移除，不调用删除接口', async () => {
  let deleted = false,
    aborted = false
  const { component, files } = createUpload(async () => {
    deleted = true
  })
  files.value[0].status = 'uploading'
  component.uploadRequests.set(1, () => {
    aborted = true
  })
  await component.handleRemove(files.value[0])
  assert.equal(aborted, true)
  assert.equal(deleted, false)
  assert.equal(files.value.length, 0)
})
