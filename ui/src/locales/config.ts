/** 定义当前支持的界面语言与偏好存储规则。 */
export const LANGUAGE_STORAGE_KEY = 'MaxKB-locale'
export const DEFAULT_LOCALE = 'zh-CN'
export const LOCALE_OPTIONS = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'zh-Hant', label: '繁體中文' },
  { value: 'en-US', label: 'English' },
] as const
export type Locale = (typeof LOCALE_OPTIONS)[number]['value']

/** Markdown 编辑器的繁体包注册为 zh-TW。 */
export const MARKDOWN_LOCALES = {
  'zh-CN': 'zh-CN',
  'zh-Hant': 'zh-TW',
  'en-US': 'en-US',
} as const satisfies Record<Locale, string>

/** 将浏览器或账号语言映射到已支持的界面语言。 */
export function normalizeLocale(language: string | null | undefined): Locale {
  const [languageCode, ...subtags] = language?.replaceAll('_', '-').toLowerCase().split('-') ?? []
  if (languageCode === 'en') return 'en-US'
  if (languageCode === 'zh') {
    // 显式文字体系优先于地区，例如 zh-Hans-HK 仍使用简体。
    if (subtags.includes('hans')) return 'zh-CN'
    if (subtags.includes('hant') || subtags.some((subtag) => ['tw', 'hk', 'mo'].includes(subtag))) return 'zh-Hant'
  }
  return DEFAULT_LOCALE
}

/** 优先读取本地偏好，其次使用浏览器语言，最终回退简体中文。 */
export function getDefaultLanguage(): Locale {
  return normalizeLocale(localStorage.getItem(LANGUAGE_STORAGE_KEY) || navigator.language)
}
