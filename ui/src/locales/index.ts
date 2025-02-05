import { useLocalStorage, usePreferredLanguages } from '@vueuse/core'
import { computed } from 'vue'
import { createI18n } from 'vue-i18n'

// 导入语言文件
const langModules = import.meta.glob('./lang/*/index.ts', { eager: true }) as Record<
  string,
  () => Promise<{ default: Object }>
>

const langModuleMap = new Map<string, Object>()

export const langCode: Array<string> = []

export const localeConfigKey = 'MaxKB-locale'

// 获取浏览器默认语言环境
const languages = usePreferredLanguages()

export function getBrowserLang() {
  const browserLang = navigator.language ? navigator.language : languages.value[0]
  let defaultBrowserLang = ''
  if (browserLang === 'zh-HK' || browserLang === 'zh-TW') {
    defaultBrowserLang = 'zh-Hant'
  } else if (browserLang === 'zh-CN') {
    defaultBrowserLang = 'zh-CN'
  } else {
    defaultBrowserLang = 'en-US'
  }
  return defaultBrowserLang
}

// 生成语言模块列表
const generateLangModuleMap = () => {
  const fullPaths = Object.keys(langModules)
  fullPaths.forEach((fullPath) => {
    const k = fullPath.replace('./lang', '')
    const startIndex = 1
    const lastIndex = k.lastIndexOf('/')
    const code = k.substring(startIndex, lastIndex)
    langCode.push(code)
    langModuleMap.set(code, langModules[fullPath])
  })
}

// 导出 Message
const importMessages = computed(() => {
  generateLangModuleMap()

  const message: Recordable = {}
  langModuleMap.forEach((value: any, key) => {
    message[key] = value.default
  })
  return message
})

export const i18n = createI18n({
  legacy: false,
  locale: useLocalStorage(localeConfigKey, getBrowserLang()).value || getBrowserLang(),
  fallbackLocale: getBrowserLang(),
  messages: importMessages.value,
  globalInjection: true
})

export const langList = computed(() => {
  if (langModuleMap.size === 0) generateLangModuleMap()

  const list: any = []
  langModuleMap.forEach((value: any, key) => {
    list.push({
      label: value.default.lang,
      value: key
    })
  })

  return list
})

// @ts-ignore
export const { t } = i18n.global

export default i18n
