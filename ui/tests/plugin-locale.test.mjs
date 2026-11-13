import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'
import dayjs from 'dayjs'
import zhCn from 'element-plus/es/locale/lang/zh-cn.mjs'
import zhTw from 'element-plus/es/locale/lang/zh-tw.mjs'
import en from 'element-plus/es/locale/lang/en.mjs'

const require = createRequire(import.meta.url)
function execute(source, dependencies) {
  const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  return exports
}
const config = execute(readFileSync(new URL('../src/locales/config.ts', import.meta.url), 'utf8'), {})
function setupComponent(path, locale, dependencies = {}) {
  const source = readFileSync(new URL(`../src/${path}`, import.meta.url), 'utf8')
  const script = compileScript(parse(source).descriptor, { id: 'plugin-locale' })
  return execute(script.content, {
    vue: Vue,
    'vue-i18n': { useI18n: () => ({ locale }) },
    '@/locales/config': config,
    ...dependencies,
  }).default.setup({}, { expose() {} })
}

for (const component of ['MdEditor', 'MdPreview']) {
  test(`${component}跟随所属入口的语言，两个入口的实例相互独立`, () => {
    const dependencies = { 'md-editor-v3': {}, './sanitize': {} }
    const adminLocale = Vue.ref('zh-CN')
    const chatLocale = Vue.ref('en-US')
    const path = `components/global/markdown-editor/${component}.vue`
    const admin = setupComponent(path, adminLocale, dependencies)
    const chat = setupComponent(path, chatLocale, dependencies)
    assert.equal(admin.language.value, 'zh-CN')
    assert.equal(chat.language.value, 'en-US')
    adminLocale.value = 'zh-Hant'
    assert.equal(admin.language.value, 'zh-TW')
    assert.equal(chat.language.value, 'en-US')
    chatLocale.value = 'zh-HK'
    assert.equal(chat.language.value, 'zh-TW')
    adminLocale.value = 'en-US'
    assert.equal(admin.language.value, 'en-US')
  })
}

test('Element Plus 和 Day.js 的三语映射一致，日期原始值和全局默认语言不变', () => {
  const initialLocale = dayjs.locale()
  const locale = Vue.ref('en-US')
  const app = setupComponent('App.vue', locale, {
    'dayjs/locale/zh-cn': require('dayjs/locale/zh-cn'),
    'dayjs/locale/zh-tw': require('dayjs/locale/zh-tw'),
    'element-plus/es/locale/lang/zh-cn': { __esModule: true, default: zhCn },
    'element-plus/es/locale/lang/zh-tw': { __esModule: true, default: zhTw },
    'element-plus/es/locale/lang/en': { __esModule: true, default: en },
    'vue-router': {},
    '@/components/global/mk-tooltip/constants': {},
  })
  const date = dayjs('2026-01-15T12:30:00')
  for (const [language, expected, month] of [
    ['zh-CN', zhCn, '一月'],
    ['zh-Hant', zhTw, '一月'],
    ['en-US', en, 'January'],
  ]) {
    locale.value = language
    assert.equal(app.elementLocale.value, expected)
    const localizedDate = date.locale(expected.name)
    assert.equal(localizedDate.format('MMMM'), month)
    assert.equal(localizedDate.valueOf(), date.valueOf())
  }
  assert.equal(dayjs.locale(), initialLocale)
})
