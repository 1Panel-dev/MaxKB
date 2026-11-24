/** 为每个应用入口创建独立的国际化实例，并连接该入口的语言状态。 */
import { watch } from 'vue'
import { createI18n } from 'vue-i18n'
import type { Locale } from './config'
import type { DefaultLocaleMessageSchema } from 'vue-i18n'
import { DEFAULT_LOCALE, LANGUAGE_STORAGE_KEY, LOCALE_OPTIONS, getLocaleNamespace, normalizeLocale } from './config'

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

interface LanguageState {
  language: string
  /** 语言缓存 key；未提供时使用 Admin 的 MaxKB-locale，为空时不同步缓存。 */
  languageStorageKey?: string
  setLanguage: (language: string) => void
}

/** 当前页面入口创建 i18n 后，供组件外的工具调用。 */
export let t: ReturnType<typeof createAppI18n>['global']['t']

/** 在应用挂载前绑定 Store；不依赖 Admin 或 Chat 的具体实现。 */
export function createAppI18n(user: LanguageState) {
  const i18n = createI18n<[DefaultLocaleMessageSchema], Locale, false>({
    legacy: false,
    globalInjection: false,
    locale: normalizeLocale(user.language),
    fallbackLocale: DEFAULT_LOCALE,
    messages: Object.fromEntries(LOCALE_OPTIONS.map(({ value }) => [value, loadMessages(value)])) as Record<Locale, DefaultLocaleMessageSchema>,
  })
  t = i18n.global.t

  watch(
    () => user.language,
    (language) => {
      const locale = normalizeLocale(language)
      i18n.global.locale.value = locale
      document.documentElement.lang = locale
    },
    { immediate: true, flush: 'sync' },
  )

  window.addEventListener('storage', (event) => {
    const languageStorageKey = user.languageStorageKey ?? LANGUAGE_STORAGE_KEY
    if (!languageStorageKey) return
    if (event.storageArea === localStorage && (event.key === languageStorageKey || event.key === null)) {
      const language = normalizeLocale(event.newValue || navigator.language)
      if (user.language !== language) user.setLanguage(language)
    }
  })
  return i18n
}
