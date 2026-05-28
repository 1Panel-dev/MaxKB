import {useLocalStorage, usePreferredLanguages} from '@vueuse/core'
import {computed, ref, watch, customRef} from 'vue'
import {createI18n} from 'vue-i18n'

// 导入语言文件
const langModules = import.meta.glob('./lang/*/index.ts', {eager: true}) as Record<
  string,
  { default: Record<string, any> }
>

type Recordable<T = any> = Record<string, T>

const langModuleMap = new Map<string, Record<string, any>>()
export const langCode: string[] = []
export const localeConfigKey = 'MaxKB-locale'

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
      console.warn('Failed to fetch external locales index, returning empty array')
      return []
    }
    if (!response.headers.get('content-type')?.includes('application/json')) {
      return []
    }

    const index = await response.json()
    return Array.isArray(index.locales) ? index.locales : []
  } catch (error) {
    console.warn('Error discovering external locales:', error)
    return []
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

/**
 * 响应式翻译字符串类
 * 使用 Proxy 包装,在任何上下文使用时都会自动获取最新翻译
 *
 * 核心特性:
 * - 透明兼容: 所有字符串操作(拼接、比较、模板插值)都正常工作
 * - 自动更新: 切换语言后,使用该对象的地方自动显示新翻译
 * - 零侵入: 无需修改现有代码,直接替换 t 函数即可
 */
// typescript
class ReactiveTranslationString {
  private _key: string
  private _params?: Record<string, any> | string

  constructor(key: string, params?: Record<string, any> | string) {
    this._key = key
    this._params = params
  }

  toString(): string {
    const globalAny = (i18n.global as unknown) as any

    if (typeof this._params === 'string') {
      try {
        return globalAny.te(this._key)
          ? String(globalAny.t(this._key))
          : String(this._params)
      } catch {
        return String(this._params)
      }
    }

    if (this._params && typeof this._params === 'object') {
      try {
        return String(globalAny.t(this._key, this._params))
      } catch {
        return String(this._key)
      }
    }

    try {
      return String(globalAny.t(this._key))
    } catch {
      return String(this._key)
    }
  }

  toJSON(): string {
    return this.toString()
  }

  valueOf(): string {
    return this.toString()
  }

  get value(): string {
    return this.toString()
  }

  [Symbol.toPrimitive](hint: string): string {
    return this.toString()
  }

  [Symbol.iterator]() {
    return this.toString()[Symbol.iterator]()
  }

  charAt(pos: number): string {
    return this.toString().charAt(pos)
  }

  charCodeAt(index: number): number {
    return this.toString().charCodeAt(index)
  }

  concat(...strings: string[]): string {
    return this.toString().concat(...strings)
  }

  indexOf(searchString: string, position?: number): number {
    return this.toString().indexOf(searchString, position)
  }

  lastIndexOf(searchString: string, position?: number): number {
    return this.toString().lastIndexOf(searchString, position)
  }

  localeCompare(that: string): number {
    return this.toString().localeCompare(that)
  }

  match(regexp: string | RegExp): RegExpMatchArray | null {
    return this.toString().match(regexp)
  }

  replace(searchValue: string | RegExp, replaceValue: string): string {
    return this.toString().replace(searchValue, replaceValue)
  }

  search(regexp: string | RegExp): number {
    return this.toString().search(regexp)
  }

  slice(start?: number, end?: number): string {
    return this.toString().slice(start, end)
  }

  split(separator: string | RegExp, limit?: number): string[] {
    return this.toString().split(separator, limit)
  }

  substring(start: number, end?: number): string {
    return this.toString().substring(start, end)
  }

  toLowerCase(): string {
    return this.toString().toLowerCase()
  }

  toUpperCase(): string {
    return this.toString().toUpperCase()
  }

  trim(): string {
    return this.toString().trim()
  }

  length: number = 0

  get [0]() { return this.toString()[0] }
}

function t(key: string, params?: Record<string, any> | string): any {
  return new ReactiveTranslationString(key, params)
}


export {t}

export default i18n
