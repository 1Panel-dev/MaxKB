/** 为每个应用入口创建独立的国际化实例，并连接该入口的语言状态。 */
import { watch } from 'vue'
import { createI18n } from 'vue-i18n'
import type { Locale } from './config'
import { DEFAULT_LOCALE, LANGUAGE_STORAGE_KEY, normalizeLocale } from './config'
import enAuth from './en-US/auth.json'
import enCommon from './en-US/common.json'
import enModel from './en-US/model.json'
import enResource from './en-US/resource.json'
import zhAuth from './zh-CN/auth.json'
import zhCommon from './zh-CN/common.json'
import zhModel from './zh-CN/model.json'
import zhResource from './zh-CN/resource.json'
import hantAuth from './zh-Hant/auth.json'
import hantCommon from './zh-Hant/common.json'
import hantModel from './zh-Hant/model.json'
import hantResource from './zh-Hant/resource.json'

type MessageSchema = { auth: typeof zhAuth; model: typeof zhModel; common: typeof zhCommon; resource: typeof zhResource }
declare module 'vue-i18n' {
  export interface DefineLocaleMessage {
    auth: MessageSchema['auth']
    model: MessageSchema['model']
    common: MessageSchema['common']
    resource: MessageSchema['resource']
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
      'zh-CN': { auth: zhAuth, model: zhModel, common: zhCommon, resource: zhResource },
      'en-US': { auth: enAuth, model: enModel, common: enCommon, resource: enResource },
      'zh-Hant': { auth: hantAuth, model: hantModel, common: hantCommon, resource: hantResource },
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
