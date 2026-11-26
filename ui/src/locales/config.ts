/** 定义界面语言、偏好存储与语言包命名空间规则。 */
import { reactive } from 'vue'
import { ADMIN_STORAGE_KEY } from '@/constants/storage-key'

export const DEFAULT_LOCALE = 'zh-CN'

export interface LocaleOption {
  label: string
  value: string
}

const BUILTIN_LOCALE_OPTIONS: LocaleOption[] = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-Hant', label: '繁體中文' },
  { value: 'en-US', label: 'English' },
]

export const LOCALE_OPTIONS = reactive<LocaleOption[]>(BUILTIN_LOCALE_OPTIONS.map((option) => ({ ...option })))
export const BUILTIN_LOCALE_CODES = new Set(BUILTIN_LOCALE_OPTIONS.map(({ value }) => value))
export type Locale = string

/** Markdown 编辑器的繁体包注册为 zh-TW。 */
export const MARKDOWN_LOCALES: Record<string, string> = {
  'zh-CN': 'zh-CN',
  'zh-Hant': 'zh-TW',
  'en-US': 'en-US',
}

/** 注册运行时部署的外置语言，重复加载时只更新显示名称。 */
export function registerLocaleOptions(options: LocaleOption[]) {
  for (const option of options) {
    const existing = LOCALE_OPTIONS.find(({ value }) => value.toLowerCase() === option.value.toLowerCase())
    if (existing) {
      existing.label = option.label
      continue
    }
    LOCALE_OPTIONS.push({ ...option })
  }
}

/** 使用 BCP 47 规则统一大小写和分隔符，非法语言代码返回 null。 */
function canonicalizeLocale(language: string | null | undefined): string | null {
  const normalizedLanguage = language?.trim().replaceAll('_', '-')
  if (!normalizedLanguage) return null
  try {
    return Intl.getCanonicalLocales(normalizedLanguage)[0] ?? null
  } catch {
    return null
  }
}

/** 分类目录不进入业务命名空间，直属 index.json 使用分类目录自身的命名空间。 */
const LOCALE_CATEGORY_DIRECTORIES = ['common', 'system']

/** 跳过分类目录后，由首个业务文件或业务目录名决定命名空间。 */
export function getLocaleNamespace(file: string): string {
  const [root, business] = file.split('/')
  const namespace = LOCALE_CATEGORY_DIRECTORIES.includes(root!) && business && business !== 'index.json' ? business : root!
  return namespace.replace(/\.json$/, '').replace(/-([a-z0-9])/g, (_, letter: string) => letter.toUpperCase())
}

/** 将浏览器或账号语言映射到已支持的界面语言。 */
export function normalizeLocale(language: string | null | undefined): Locale {
  const canonicalLanguage = canonicalizeLocale(language)
  if (!canonicalLanguage) return DEFAULT_LOCALE

  const exactOption = LOCALE_OPTIONS.find(({ value }) => value.toLowerCase() === canonicalLanguage.toLowerCase())
  if (exactOption) return exactOption.value

  const [languageCode, ...subtags] = canonicalLanguage.toLowerCase().split('-')
  if (languageCode === 'en') return 'en-US'
  if (languageCode === 'zh') {
    // 显式文字体系优先于地区，例如 zh-Hans-HK 仍使用简体。
    if (subtags.includes('hans')) return 'zh-CN'
    if (subtags.includes('hant') || subtags.some((subtag) => ['tw', 'hk', 'mo'].includes(subtag))) return 'zh-Hant'
  }
  const baseMatches = LOCALE_OPTIONS.filter(({ value }) => value.toLowerCase().split('-')[0] === languageCode)
  if (baseMatches.length === 1) return baseMatches[0]!.value
  return canonicalLanguage
}

/** 运行时语言加载完成后，仅保留已注册语言；未部署的语言回落默认语言。 */
export function resolveSupportedLocale(language: string | null | undefined): Locale {
  const locale = normalizeLocale(language)
  return LOCALE_OPTIONS.find(({ value }) => value.toLowerCase() === locale.toLowerCase())?.value ?? DEFAULT_LOCALE
}

/** Markdown 编辑器没有对应语言包时使用默认语言。 */
export function getMarkdownLocale(language: string | null | undefined): string {
  return MARKDOWN_LOCALES[normalizeLocale(language)] ?? DEFAULT_LOCALE
}

/** 优先读取本地偏好，其次使用浏览器语言，最终回退简体中文。 */
export function getDefaultLanguage(): Locale {
  return normalizeLocale(localStorage.getItem(ADMIN_STORAGE_KEY.LANGUAGE) || navigator.language)
}
