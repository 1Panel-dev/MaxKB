import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import { compileScript, parse } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as Vue from 'vue'
import { createI18n } from 'vue-i18n'

const messages = Object.fromEntries(
  ['zh-CN', 'zh-Hant', 'en-US'].map((locale) => [
    locale,
    {
      auth: JSON.parse(readFileSync(new URL(`../src/locales/${locale}/auth.json`, import.meta.url), 'utf8')),
    },
  ]),
)

function flattenMessages(value, prefix = '') {
  return Object.fromEntries(
    Object.entries(value).flatMap(([key, child]) => {
      const path = prefix ? `${prefix}.${key}` : key
      return typeof child === 'object' ? Object.entries(flattenMessages(child, path)) : [[path, child]]
    }),
  )
}

test('认证语言包的 key、插值参数和非空文案保持一致', () => {
  const reference = flattenMessages(messages['zh-CN'])
  for (const locale of ['zh-Hant', 'en-US']) {
    const translated = flattenMessages(messages[locale])
    assert.deepEqual(Object.keys(translated).sort(), Object.keys(reference).sort())
    for (const [key, text] of Object.entries(translated)) {
      assert.ok(text.trim(), `${locale}: ${key}`)
      assert.deepEqual(
        [...text.matchAll(/\{(\w+)\}/g)].map((match) => match[1]).sort(),
        [...reference[key].matchAll(/\{(\w+)\}/g)].map((match) => match[1]).sort(),
        `${locale}: ${key}`,
      )
    }
  }
})

// 执行实际组件 setup，仅替换浏览器、网络及生命周期依赖。
function setupComponent(path, composer, user = {}, currentUserApi = {}) {
  const source = readFileSync(new URL(`../src/${path}`, import.meta.url), 'utf8')
  const script = compileScript(parse(source).descriptor, { id: 'auth-locale' })
  const { outputText } = ts.transpileModule(script.content, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    if (id === 'vue') return { ...Vue, onMounted() {}, useTemplateRef: () => Vue.ref() }
    if (id === 'vue-i18n') return { useI18n: () => composer }
    if (id === 'vue-router') return { useRoute: () => ({ query: {} }), useRouter: () => ({}) }
    if (id === '@/stores') return { useStore: () => ({ user, auth: {}, theme: {} }) }
    if (id === '@/api/admin/auth/current-user') return { __esModule: true, default: currentUserApi }
    if (id === '@/api/enums') return { LOGIN_METHOD: { LOCAL: 'LOCAL', LDAP: 'LDAP' } }
    if (
      id.endsWith('.vue') ||
      id.startsWith('@/api/') ||
      id.startsWith('@/locales/') ||
      id.startsWith('@/permission/') ||
      id === '@/utils/message' ||
      id === 'jsencrypt' ||
      id === '../constants'
    )
      return {}
    assert.fail(`Unexpected dependency: ${id}`)
  }, exports)
  return exports.default.setup({ preview: true, loginService: {} }, { expose() {} })
}

for (const [name, path, formKey, refKey, rulesKey, field, key] of [
  [
    '账号登录',
    'views/login/modes/AccountLogin.vue',
    'accountLoginForm',
    'accountLoginFormRef',
    'accountLoginRules',
    'username',
    'auth.credentials.validation.usernameRequired',
  ],
  [
    '找回密码',
    'views/login/forgot-password/index.vue',
    'forgotPasswordForm',
    'forgotPasswordFormRef',
    'forgotPasswordRules',
    'email',
    'auth.forgotPassword.validation.emailRequired',
  ],
]) {
  test(`${name}切换语言保留输入，仅刷新已显示的校验错误`, async () => {
    const composer = createI18n({ legacy: false, locale: 'zh-CN', messages }).global
    const scope = Vue.effectScope()
    const component = scope.run(() => setupComponent(path, composer))
    component[formKey][field] = 'kept-input'
    const validated = []
    component[refKey].value = {
      fields: [
        { prop: field, validateState: 'error' },
        { prop: 'password', validateState: '' },
      ],
      validateField: async (prop) => validated.push(prop),
    }
    for (const locale of ['en-US', 'zh-Hant']) {
      composer.locale.value = locale
      await Vue.nextTick()
      assert.equal(component[formKey][field], 'kept-input')
      assert.equal(component[rulesKey].value[field][0].message, composer.t(key))
    }
    assert.deepEqual(validated, [field, field])
    scope.stop()
  })
}

test('头部切换语言在账号保存成功后生效，失败不覆盖原偏好', async () => {
  const user = Vue.reactive({
    language: 'zh-CN',
    userInfo: { language: 'zh-CN' },
    setLanguage(language) {
      this.language = language
    },
  })
  let resolveRequest
  let rejectRequest
  const requests = []
  const component = setupComponent('layout/avatar-dropdown/index.vue', { t: (key) => key }, user, {
    postCurrentUserLanguage(language) {
      requests.push(language)
      return new Promise((resolve, reject) => {
        resolveRequest = resolve
        rejectRequest = reject
      })
    },
  })
  const first = component.handleChangeLanguage('en-US')
  assert.equal(user.language, 'zh-CN')
  component.handleChangeLanguage('zh-Hant')
  assert.deepEqual(requests, ['en-US'])
  resolveRequest()
  await first
  assert.equal(user.language, 'en-US')
  assert.equal(user.userInfo.language, 'en-US')
  const second = component.handleChangeLanguage('zh-Hant')
  rejectRequest(new Error('save failed'))
  await assert.rejects(second)
  assert.equal(user.language, 'en-US')
  assert.equal(component.isChangingLanguage.value, false)
})
