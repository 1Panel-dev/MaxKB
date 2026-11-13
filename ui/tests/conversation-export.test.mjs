import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import ts from 'typescript'
import * as Vue from 'vue'

function loadExport(messages) {
  const source = readFileSync(
    new URL('../src/conversation-panel/components/header/header-actions/export/use-conversation-export.ts', import.meta.url),
    'utf8',
  )
  const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } })
  const store = { messages: Vue.ref(messages), loading: Vue.ref(false), streamLoading: Vue.ref(false) }
  const downloads = []
  const blobs = []
  const errors = []
  const dependencies = {
    vue: Vue,
    dompurify: { sanitize: (html) => html },
    '../../../message-list/index': { useMessageListStore: () => store },
    '../../../../left-sidebar/conversation-list/index': {
      useConversationListStore: () => ({ currentConversation: Vue.ref({ abstract: '测试/对话' }), currentChatId: Vue.ref('chat-id') }),
    },
    '@/utils/message': { MsgError: (message) => errors.push(message) },
  }
  const module = { exports: {} }
  compileFunction(outputText, ['require', 'exports', 'module', 'document', 'URL', 'setTimeout'])(
    (id) => dependencies[id],
    module.exports,
    module,
    {
      createElement: () => {
        const link = { click: () => downloads.push(link.download) }
        return link
      },
    },
    {
      createObjectURL: (blob) => {
        blobs.push(blob)
        return 'blob:test'
      },
      revokeObjectURL() {},
    },
    (callback) => callback(),
  )
  return { ...module.exports.useConversationExport(), store, downloads, blobs, errors }
}

test('Markdown 保留已加载问答、嵌套正文和附件，跳过思考及工具参数', async () => {
  const exporter = loadExport([
    { role: 'USER', content: [{ type: 'QUESTION', content: '问题', image_list: [{ name: '图片', url: 'https://example.com/image.png' }] }] },
    {
      role: 'ASSISTANT',
      content: [
        { type: 'REASONING', content: '隐藏思考' },
        { type: 'TOOL', arguments: '隐藏参数' },
        { type: 'GROUP', children: [{ type: 'TEXT', content: '**回答**' }] },
        { type: 'HTML', content: '<p>页面</p>' },
      ],
    },
  ])
  await exporter.exportText('markdown')
  const markdown = await exporter.blobs[0].text()
  assert.match(markdown, /## 用户\n\n问题/)
  assert.match(markdown, /!\[图片\]\(<https:\/\/example.com\/image.png>\)/)
  assert.match(markdown, /## 助手\n\n\*\*回答\*\*/)
  assert.match(markdown, /```html\n<p>页面<\/p>\n```/)
  assert.doesNotMatch(markdown, /隐藏思考|隐藏参数/)
  assert.deepEqual(exporter.downloads, ['测试_对话.md'])
  assert.equal(exporter.loading.value, false)
})

test('无消息、加载历史或生成中均不发起导出', async () => {
  const exporter = loadExport([])
  await exporter.exportText('markdown')
  exporter.store.messages.value = [{ role: 'USER', content: [{ type: 'QUESTION', content: '问题' }] }]
  exporter.store.loading.value = true
  await exporter.exportText('markdown')
  exporter.store.loading.value = false
  exporter.store.streamLoading.value = true
  await exporter.exportText('markdown')
  assert.equal(exporter.downloads.length, 0)
  assert.equal(exporter.disabled.value, true)
})

test('操作收纳仅在移动端超过一个时启用，Fragment 中的外部操作一起计数', () => {
  const source = readFileSync(new URL('../src/conversation-panel/components/header/header-actions/index.vue', import.meta.url), 'utf8').match(
    /<script lang="ts">([\s\S]*?)<\/script>/,
  )[1]
  const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } })
  const module = { exports: {} }
  const Dropdown = { name: 'Dropdown' }
  const dependencies = {
    vue: Vue,
    '@/components/global/mk-dropdown/index.vue': Dropdown,
    '@/components/global/mk-dropdown/MkDropdownMenu.vue': { name: 'Menu' },
    '@/components/global/mk-icon/index.vue': { name: 'Icon' },
    'element-plus': { ElButton: { name: 'Button' } },
    '@/utils/vnode': { hasRenderableSlotContent: (node) => node.type !== Vue.Comment && (node.type !== Vue.Text || node.children.trim()) },
  }
  compileFunction(outputText, ['require', 'exports', 'module'])((id) => dependencies[id], module.exports, module)
  const Action = { name: 'Action' }
  const externalAction = Vue.h(Action, { disabled: true, onClick() {} })
  const children = [Vue.h(Action), Vue.h(Vue.Fragment, [Vue.createCommentVNode('hidden'), externalAction])]
  const render = (collapse, actions = children) => module.exports.default.setup({ collapse }, { slots: { default: () => actions } })()
  const desktop = render(false)
  assert.equal(desktop.type, Vue.Fragment)
  assert.equal(desktop.children.length, 2)
  assert.equal(desktop.children[1].props.display, 'button')
  assert.equal(desktop.children[1].props.onClick, externalAction.props.onClick)
  assert.equal(desktop.children[1].props.disabled, true)
  const mobile = render(true)
  assert.equal(mobile.type, Dropdown)
  assert.equal(mobile.props.persistent, true)
  const menu = mobile.children.dropdown()
  assert.equal(menu.children.default()[1].props.display, 'menu')
  assert.equal(render(true, [Vue.h(Action)]).type, Vue.Fragment)
})
