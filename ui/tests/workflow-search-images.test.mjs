import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import { renderToString } from '@vue/server-renderer'
import ts from 'typescript'
import * as Vue from 'vue'

const filename = new URL('../src/workflow-canvas/nodes/search-knowledge-node/details/index.vue', import.meta.url)
const { descriptor } = parse(readFileSync(filename, 'utf8'))
const script = compileScript(descriptor, { id: 'workflow-search-images-test', inlineTemplate: true })
const { outputText } = ts.transpileModule(script.content, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
})
const SlotContainer = {
  inheritAttrs: false,
  setup:
    (_, { slots }) =>
    () =>
      slots.default?.(),
}
const dependencies = {
  vue: Vue,
  '@/workflow-canvas/execution-details/DetailContainer.vue': SlotContainer,
  '@/workflow-canvas/execution-details/BaseHeader.vue': SlotContainer,
  '@/utils/common': { getFileUrl: (fileId) => (fileId ? `./oss/file/${fileId}` : '') },
  '@/utils/icon': { getFileIconUrl: () => 'document-icon.svg' },
  '@/api/enums': { DOCUMENT_RESOURCE_TYPE: { IMAGE: 'image', DOCUMENT: 'document' } },
  '@/assets/file-type/file-image-icon.svg': 'image-icon.svg',
}
const exports = {}
compileFunction(outputText, ['require', 'exports'])((id) => {
  assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
  return dependencies[id]
}, exports)

// 渲染实际详情模板，替换折叠容器和公共 UI，以检查传给图片组件的地址及预览配置。
async function renderParagraph(paragraph) {
  const app = Vue.createSSRApp(exports.default, { data: { paragraph_list: [{ title: 'google', similarity: 0.918, ...paragraph }] } })
  app.component('el-scrollbar', SlotContainer)
  app.component('el-image', {
    props: ['src', 'previewSrcList'],
    setup: (props) => () => Vue.h('img', { src: props.src, 'data-preview': props.previewSrcList?.[0] }),
  })
  app.component('MdPreview', { props: ['modelValue'], setup: (props) => () => Vue.h('p', props.modelValue) })
  app.component('KnowledgeIcon', { render: () => null })
  return renderToString(app)
}

test('图片文档命中文本向量仍展示原图并支持预览', async () => {
  const html = await renderParagraph({
    content: 'google',
    document_name: 'google.png',
    document_resource_type: 'image',
    document_image_id: 'original-image',
    hit_asset: null,
    hit_unit_type: 'text',
  })
  assert.match(html, /src="\.\/oss\/file\/original-image"/)
  assert.match(html, /data-preview="\.\/oss\/file\/original-image"/)
  assert.match(html, /src="image-icon.svg"/)
  assert.match(html, /<p[^>]*>google<\/p>/)
})

test('普通文档展示命中资产图片', async () => {
  const html = await renderParagraph({ content: 'chart', document_resource_type: 'document', hit_asset: { file_id: 'chart-image' } })
  assert.match(html, /src="\.\/oss\/file\/chart-image"/)
})

test('正文已经包含图片时不添加重复缩略图', async () => {
  const html = await renderParagraph({ content: '![chart](./oss/file/chart-image)', hit_asset: { file_id: 'chart-image' } })
  assert.doesNotMatch(html, /data-preview=/)
})

test('纯文本结果和缺失原图地址的旧数据正常渲染', async () => {
  for (const paragraph of [{ content: 'plain text' }, { content: 'plain text', document_resource_type: 'image' }]) {
    const html = await renderParagraph(paragraph)
    assert.doesNotMatch(html, /data-preview=/)
    assert.match(html, /<p[^>]*>plain text<\/p>/)
  }
})
