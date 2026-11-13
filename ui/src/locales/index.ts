/** 为每个应用入口创建独立的国际化实例，并连接该入口的语言状态。 */
import { watch } from 'vue'
import { createI18n } from 'vue-i18n'
import { DEFAULT_LOCALE, LANGUAGE_STORAGE_KEY, normalizeLocale, type Locale } from './config'
import zhAuth from './zh-CN/auth.json'
import enAuth from './en-US/auth.json'
import hantAuth from './zh-Hant/auth.json'

type MessageSchema = { auth: typeof zhAuth }
declare module 'vue-i18n' {
  export interface DefineLocaleMessage {
    auth: MessageSchema['auth']
  }
}

interface LanguageState {
  language: string
  setLanguage: (language: string) => void
}

/** 在应用挂载前绑定 Store；不依赖 Admin 或 Chat 的具体实现。 */
export function createAppI18n(user: LanguageState) {
  const i18n = createI18n<[MessageSchema], Locale, false>({
    legacy: false,
    globalInjection: false,
    locale: normalizeLocale(user.language),
    fallbackLocale: DEFAULT_LOCALE,
    messages: {
      'zh-CN': { auth: zhAuth },
      'en-US': { auth: enAuth },
      'zh-Hant': { auth: hantAuth },
    },
  })

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
    if (event.storageArea === localStorage && (event.key === LANGUAGE_STORAGE_KEY || event.key === null)) {
      const language = normalizeLocale(event.newValue || navigator.language)
      if (user.language !== language) user.setLanguage(language)
    }
  })
  return i18n
}
