/** 为每个应用入口创建独立的国际化实例，并连接该入口的语言状态。 */
import { watch } from 'vue'
import { createI18n } from 'vue-i18n'
import type { Locale } from './config'
import type { DefaultLocaleMessageSchema } from 'vue-i18n'
import { BUILTIN_LOCALE_CODES, DEFAULT_LOCALE, LOCALE_OPTIONS, getLocaleNamespace, normalizeLocale, resolveSupportedLocale } from './config'
import { getRuntimeLocaleMessages, loadRuntimeLocales } from './runtime'
import { ADMIN_STORAGE_KEY } from '@/constants/storage-key'

const localeFiles = import.meta.glob<Record<string, unknown>>('./*/**/*.json', { eager: true, import: 'default' })

function loadMessages(locale: Locale) {
  const prefix = `./${locale}/`
  const domains: Record<string, Record<string, unknown>> = {}
  for (const [path, messages] of Object.entries(localeFiles)) {
    if (!path.startsWith(prefix)) continue
    const domain = getLocaleNamespace(path.slice(prefix.length))
    Object.assign((domains[domain] ??= {}), messages)
  }
  return domains
}

function getRuntimeLocaleBaseUrl() {
  return import.meta.env.VITE_APP_NAME === 'chat' ? '/static/chat/locales' : '/static/admin/locales'
}

interface LanguageState {
  language: string
  setLanguage: (language: string) => void
}

/** 当前页面入口创建 i18n 后，供组件外的工具调用。 */
export let t: ReturnType<typeof createAppI18n>['global']['t']

/** 在应用挂载前绑定 Store；语言缓存 key 为 null 时不监听浏览器缓存变化。 */
export function createAppI18n(user: LanguageState, languageStorageKey: string | null = ADMIN_STORAGE_KEY.LANGUAGE) {
  const i18n = createI18n<[DefaultLocaleMessageSchema], Locale, false>({
    legacy: false,
    globalInjection: false,
    locale: normalizeLocale(user.language),
    fallbackLocale: DEFAULT_LOCALE,
    messages: Object.fromEntries([...BUILTIN_LOCALE_CODES].map((locale) => [locale, loadMessages(locale)])) as Record<
      Locale,
      DefaultLocaleMessageSchema
    >,
  })
  t = i18n.global.t

  let runtimeLocalesLoaded = false
  const applyLocale = () => {
    const locale = runtimeLocalesLoaded ? resolveSupportedLocale(user.language) : normalizeLocale(user.language)
    i18n.global.locale.value = locale
    document.documentElement.lang = locale
  }

  watch(() => user.language, applyLocale, { immediate: true, flush: 'sync' })

  void loadRuntimeLocales(getRuntimeLocaleBaseUrl()).then(() => {
    for (const { value: locale } of LOCALE_OPTIONS) {
      const messages = getRuntimeLocaleMessages(locale)
      if (messages) i18n.global.mergeLocaleMessage(locale, messages as DefaultLocaleMessageSchema)
    }
    runtimeLocalesLoaded = true
    applyLocale()
  })

  if (languageStorageKey)
    window.addEventListener('storage', (event) => {
      if (event.storageArea === localStorage && (event.key === languageStorageKey || event.key === null)) {
        const sourceLanguage = event.newValue || navigator.language
        const language = runtimeLocalesLoaded ? resolveSupportedLocale(sourceLanguage) : normalizeLocale(sourceLanguage)
        if (user.language !== language) user.setLanguage(language)
      }
    })
  return i18n
}
