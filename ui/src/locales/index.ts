import { useLocalStorage, usePreferredLanguages } from '@vueuse/core'
import { computed } from 'vue'
import { createI18n } from 'vue-i18n'

// 导入语言文件
const langModules = import.meta.glob('./lang/*/index.ts', { eager: true }) as Record<
  string,
  { default: Record<string, any> }
>

type Recordable<T = any> = Record<string, T>

const langModuleMap = new Map<string, Record<string, any>>()
export const langCode: string[] = []
export const localeConfigKey = 'MaxKB-locale'

const DEFAULT_EXTERNAL_LOCALES = [
  'ja',
  'ko-KR',
  'de-DE',
  'fr-FR',
  'es-ES',
  'ru-RU',
  'pt-BR',
  'it-IT',
  'th-TH',
  'vi-VN'
]

const languages = usePreferredLanguages()

export function getBrowserLang() {
  const browserLang = navigator.language || languages.value[0] || 'en-US'

  if (browserLang === 'zh-HK' || browserLang === 'zh-TW') {
    return 'zh-Hant'
  }

  if (browserLang === 'zh-CN') {
    return 'zh-CN'
  }

  return 'en-US'
}

function generateLangModuleMap() {
  if (langModuleMap.size > 0) return

  Object.keys(langModules).forEach((fullPath) => {
    const code = fullPath.replace('./lang/', '').replace('/index.ts', '')
    const module = langModules[fullPath]
    langModuleMap.set(code, module.default)
    if (!langCode.includes(code)) {
      langCode.push(code)
    }
  })
}

const importMessages = computed(() => {
  generateLangModuleMap()

  const message: Recordable = {}
  langModuleMap.forEach((value, key) => {
    message[key] = value
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

// 外置语言包目录（相对于 public 目录）
const EXTERNAL_LOCALES_DIR = `${window.MaxKB?.prefix || '/chat'}/locales`

async function discoverExternalLocales(): Promise<string[]> {
  try {
    const response = await fetch(`${EXTERNAL_LOCALES_DIR}/index.json`)
    if (!response.ok) {
      return DEFAULT_EXTERNAL_LOCALES
    }

    const index = await response.json()
    return Array.isArray(index.locales) ? index.locales : DEFAULT_EXTERNAL_LOCALES
  } catch {
    return DEFAULT_EXTERNAL_LOCALES
  }
}

async function loadExternalLocale(localeCode: string): Promise<Record<string, any> | null> {
  try {
    const response = await fetch(`${EXTERNAL_LOCALES_DIR}/${localeCode}.json`)
    if (!response.ok) {
      return null
    }
    return await response.json()
  } catch {
    return null
  }
}

export async function initExternalLocales(): Promise<void> {
  const availableLocales = await discoverExternalLocales()

  for (const code of availableLocales) {
    if (langModuleMap.has(code)) continue

    const data = await loadExternalLocale(code)
    if (!data) continue

    i18n.global.setLocaleMessage(code, data)

    if (!langCode.includes(code)) {
      langCode.push(code)
    }
  }
}

export const langList = computed(() => {
  generateLangModuleMap()

  const list: Array<{ label: string; value: string }> = []

  langModuleMap.forEach((value, key) => {
    list.push({
      label: value.lang || key,
      value: key
    })
  })

  langCode.forEach((locale) => {
    if (langModuleMap.has(locale)) return
    const messages = i18n.global.getLocaleMessage(locale) as Record<string, any>
    list.push({
      label: messages?.lang || locale,
      value: locale
    })
  })

  return list
})

export const { t } = i18n.global

export default i18n
