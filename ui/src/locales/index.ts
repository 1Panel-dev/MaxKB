/** 为每个应用入口创建独立的国际化实例，并连接该入口的语言状态。 */
import { watch } from 'vue'
import { createI18n } from 'vue-i18n'
import { DEFAULT_LOCALE, LANGUAGE_STORAGE_KEY, normalizeLocale, type Locale } from './config'
import zhAuth from './zh-CN/auth.json'
import enAuth from './en-US/auth.json'
import hantAuth from './zh-Hant/auth.json'
import zhCommon from './zh-CN/common.json'
import enCommon from './en-US/common.json'
import hantCommon from './zh-Hant/common.json'
import zhComponents from './zh-CN/components.json'
import enComponents from './en-US/components.json'
import hantComponents from './zh-Hant/components.json'
import zhModel from './zh-CN/model.json'
import enModel from './en-US/model.json'
import hantModel from './zh-Hant/model.json'
import zhDynamicForm from './zh-CN/dynamic-form.json'
import enDynamicForm from './en-US/dynamic-form.json'
import hantDynamicForm from './zh-Hant/dynamic-form.json'
import zhIdentity from './zh-CN/system/identity.json'
import enIdentity from './en-US/system/identity.json'
import hantIdentity from './zh-Hant/system/identity.json'
import zhResourceManagement from './zh-CN/system/resource-management.json'
import enResourceManagement from './en-US/system/resource-management.json'
import hantResourceManagement from './zh-Hant/system/resource-management.json'
import zhSharedResources from './zh-CN/system/shared-resources.json'
import enSharedResources from './en-US/system/shared-resources.json'
import hantSharedResources from './zh-Hant/system/shared-resources.json'

type MessageSchema = {
  auth: typeof zhAuth
  common: typeof zhCommon
  components: typeof zhComponents
  model: typeof zhModel
  dynamicForm: typeof zhDynamicForm
  system: {
    identity: typeof zhIdentity
    resourceManagement: typeof zhResourceManagement
    sharedResources: typeof zhSharedResources
  }
}
declare module 'vue-i18n' {
  export interface DefineLocaleMessage {
    auth: MessageSchema['auth']
    common: MessageSchema['common']
    components: MessageSchema['components']
    model: MessageSchema['model']
    dynamicForm: MessageSchema['dynamicForm']
    system: MessageSchema['system']
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
      'zh-CN': {
        auth: zhAuth,
        common: zhCommon,
        components: zhComponents,
        model: zhModel,
        dynamicForm: zhDynamicForm,
        system: { identity: zhIdentity, resourceManagement: zhResourceManagement, sharedResources: zhSharedResources },
      },
      'en-US': {
        auth: enAuth,
        common: enCommon,
        components: enComponents,
        model: enModel,
        dynamicForm: enDynamicForm,
        system: { identity: enIdentity, resourceManagement: enResourceManagement, sharedResources: enSharedResources },
      },
      'zh-Hant': {
        auth: hantAuth,
        common: hantCommon,
        components: hantComponents,
        model: hantModel,
        dynamicForm: hantDynamicForm,
        system: { identity: hantIdentity, resourceManagement: hantResourceManagement, sharedResources: hantSharedResources },
      },
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
