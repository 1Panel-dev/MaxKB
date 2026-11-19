/** 定义界面语言、偏好存储与语言包命名空间规则。 */
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
