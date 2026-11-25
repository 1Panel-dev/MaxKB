/** 加载后端部署在 static 目录中的外置语言包。 */
import { BUILTIN_LOCALE_CODES, registerLocaleOptions } from './config'

export interface RuntimeLocalePackage {
  label: string
  locale: string
  messages: Record<string, unknown>
}

type JsonFetcher = (url: string, init?: RequestInit) => Promise<Response>

const runtimeLocaleMessages = new Map<string, Record<string, unknown>>()
const LOCALE_CODE_PATTERN = /^[a-z]{2,3}(?:-[a-z0-9]{1,8})*$/i

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

async function fetchJson(url: string, fetcher: JsonFetcher): Promise<unknown> {
  const response = await fetcher(url, { cache: 'no-cache' })
  if (!response.ok) throw new Error(`Failed to load locale resource: ${url}`)
  return response.json()
}

/** 拒绝可能被拼接为其他静态资源路径的语言代码。 */
export function isRuntimeLocaleCode(value: unknown): value is string {
  return typeof value === 'string' && LOCALE_CODE_PATTERN.test(value)
}

export function getRuntimeLocaleMessages(locale: string): Record<string, unknown> | undefined {
  return runtimeLocaleMessages.get(locale)
}

/** 加载索引及语言包；单个语言失败时跳过，不影响内置语言使用。 */
export async function loadRuntimeLocales(baseUrl: string, fetcher: JsonFetcher = (url, init) => fetch(url, init)) {
  const normalizedBaseUrl = baseUrl.replace(/\/+$/, '')
  let index: unknown
  try {
    index = await fetchJson(`${normalizedBaseUrl}/index.json`, fetcher)
  } catch {
    return
  }
  if (!isRecord(index) || !Array.isArray(index.locales)) return

  const localeCodes = [...new Set(index.locales.filter(isRuntimeLocaleCode))].filter((locale) => !BUILTIN_LOCALE_CODES.has(locale))
  const packages = await Promise.all(
    localeCodes.map(async (locale): Promise<RuntimeLocalePackage | null> => {
      try {
        const data = await fetchJson(`${normalizedBaseUrl}/${locale}.json`, fetcher)
        if (!isRecord(data)) return null
        const { lang, ...messages } = data
        return {
          label: typeof lang === 'string' && lang.trim() ? lang.trim() : locale,
          locale,
          messages,
        }
      } catch {
        return null
      }
    }),
  )

  for (const localePackage of packages) {
    if (!localePackage) continue
    runtimeLocaleMessages.set(localePackage.locale, localePackage.messages)
    registerLocaleOptions([{ label: localePackage.label, value: localePackage.locale }])
  }
}
