import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'

function load(path, resolveDependency) {
  let source = readFileSync(new URL(`../src/${path}`, import.meta.url), 'utf8')
  if (path.endsWith('.vue')) source = compileScript(parse(source).descriptor, { id: 'image-upload' }).content
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])(resolveDependency, exports)
  return exports
}

function createUpload(scope) {
  const requests = []
  const emitted = []
  const strategy = { image_understand: { enable: false } }
  const refs = {
    processingRef: Vue.ref({ validate: async () => true, getStrategy: () => strategy }),
    previewRef: Vue.ref({ validate: () => true }),
  }
  function dependency(id) {
    if (id === 'vue') return { ...Vue, provide() {}, useTemplateRef: (key) => refs[key] ?? Vue.ref() }
    if (id === 'vue-router') return { useRoute: () => ({ meta: { resourceScope: scope }, params: { knowledgeId: 'knowledge-a' } }) }
    if (id === '@/utils/resource-context') return { getResourceScope: () => scope }
    if (id === '@/utils/message') return { MsgSuccess() {}, MsgWarning() {} }
    if (id === '@/api/admin/core/request')
      return Object.fromEntries(
        ['post', 'put'].map((method) => [
          method,
          async (url, payload) => {
            requests.push({ method, url, payload })
            return [{ source_file_id: 'image-a', resource_type: 'image', name: 'image.png', content: [{ title: 'image', content: '识别内容' }] }]
          },
        ]),
      )
    if (id.startsWith('@/api/') && id.endsWith('/image')) return load(`${id.slice(2)}.ts`, dependency)
    if (id === '@/components/mk-drag-upload/validation') return { getUploadValidationMessage: () => undefined }
    if (id.endsWith('.vue') || id.startsWith('@/api/') || id.startsWith('@/constants/')) return {}
    assert.fail(`Unexpected dependency: ${id}`)
  }
  const { provideKnowledgeDetailContext } = load('views/knowledge-detail/context.ts', dependency)
  const context = provideKnowledgeDetailContext({ knowledge: Vue.computed(() => undefined), replaceKnowledgeDetail() {} })
  const component = load('views/knowledge-detail/library/image/upload-image/UploadImageDrawer.vue', dependency).default
  const drawer = component.setup(
    { api: context.resourceApi.image, knowledgeId: 'knowledge-a' },
    { expose() {}, emit: (...args) => emitted.push(args) },
  )
  drawer.selectedFiles.value = [{ status: 'success', file_id: 'image-a' }]
  drawer.open()
  return { drawer, requests, emitted, strategy, api: context.resourceApi.image }
}

for (const [scope, prefix] of [
  ['system-resource', '/system/resource/knowledge'],
  ['system-shared', '/system/shared/knowledge'],
]) {
  test(`${scope} 图片生成预览后可导入并刷新列表`, async () => {
    const { drawer, requests, emitted, strategy } = createUpload(scope)
    await drawer.handleGeneratePreview()
    assert.equal(drawer.previewVisible.value, true)
    await drawer.handleSubmit()
    assert.deepEqual(requests, [
      { method: 'post', url: `${prefix}/knowledge-a/document/image/preview`, payload: { file_id_list: ['image-a'], doc_strategy: strategy } },
      {
        method: 'put',
        url: `${prefix}/knowledge-a/document/image/batch_create`,
        payload: { file_id_list: ['image-a'], preview_list: [{ source_file_id: 'image-a', content: [{ title: 'image', content: '识别内容' }] }] },
      },
    ])
    assert.deepEqual(emitted, [['refresh']])
    assert.equal(drawer.visible.value, false)
    assert.equal(drawer.loading.value, false)
  })
}

test('系统共享图片不生成预览时直接携带策略导入', async () => {
  const { drawer, requests, strategy } = createUpload('system-shared')
  await drawer.handleSubmit()
  assert.deepEqual(requests, [
    {
      method: 'put',
      url: '/system/shared/knowledge/knowledge-a/document/image/batch_create',
      payload: { file_id_list: ['image-a'], doc_strategy: strategy },
    },
  ])
})

test('图片预览导入携带编辑后的标题、正文和关联问题', async () => {
  const { drawer, requests } = createUpload('system-shared')
  await drawer.handleGeneratePreview()
  const paragraph = { title: '编辑标题', content: '编辑正文', problem_list: [{ content: '图片里有什么？' }] }
  drawer.previewDocuments.value[0].content = [paragraph]
  await drawer.handleSubmit()
  assert.deepEqual(requests.at(-1).payload, {
    file_id_list: ['image-a'],
    preview_list: [{ source_file_id: 'image-a', content: [paragraph] }],
  })
})

test('工作空间共享知识库不提供图片写入 API', () => {
  assert.equal(createUpload('workspace-shared').api, undefined)
})
