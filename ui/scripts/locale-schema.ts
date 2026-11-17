/** 从默认语言生成 Vue I18n 类型，并在类型检查时校验各语言包。 */
import { existsSync, readFileSync, readdirSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { DEFAULT_LOCALE, LOCALE_OPTIONS, getLocaleNamespace } from '../src/locales/config.ts'

const localeRoot = fileURLToPath(new URL('../src/locales/', import.meta.url))
export const schemaSourceDir = join(localeRoot, DEFAULT_LOCALE)

function jsonFiles(directory: string) {
  return readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.json'))
    .map((entry) => entry.name)
    .sort()
}

export function generateLocaleSchema() {
  const domains = new Map<string, string>()
  for (const file of jsonFiles(schemaSourceDir)) {
    const domain = getLocaleNamespace(file)
    if (domains.has(domain)) throw new Error(`语言包 ${domains.get(domain)} 和 ${file} 使用了相同的命名空间 ${domain}`)
    domains.set(domain, file)
  }
  const fields = Array.from(
    domains,
    ([domain, file]) => `    ${JSON.stringify(domain)}: typeof import(${JSON.stringify(`./${DEFAULT_LOCALE}/${file}`)})`,
  )
  const schema = [
    '// 由 scripts/locale-schema.ts 根据默认语言的 JSON 文件生成。',
    "import 'vue-i18n'",
    '',
    "declare module 'vue-i18n' {",
    '  interface DefineLocaleMessage {',
    ...fields,
    '  }',
    '}',
    '',
  ].join('\n')
  const output = join(localeRoot, 'schema.generated.d.ts')
  if (existsSync(output) && readFileSync(output, 'utf8') === schema) return
  const temp = `${output}.${process.pid}.tmp`
  writeFileSync(temp, schema)
  renameSync(temp, output)
}

function collectKeys(value: unknown, prefix: string, keys: Map<string, string>) {
  const kind = value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value
  keys.set(prefix, kind)
  if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) collectKeys(child, `${prefix}.${key}`, keys)
  }
}

function localeKeys(locale: string) {
  const directory = join(localeRoot, locale)
  const keys = new Map<string, string>()
  for (const file of jsonFiles(directory)) {
    const path = join(directory, file)
    try {
      collectKeys(JSON.parse(readFileSync(path, 'utf8')), file, keys)
    } catch (error) {
      throw new Error(`无法读取语言包 ${path}`, { cause: error })
    }
  }
  return keys
}

if (import.meta.main) {
  const expected = localeKeys(DEFAULT_LOCALE)
  for (const { value: locale } of LOCALE_OPTIONS) {
    if (locale === DEFAULT_LOCALE) continue
    const actual = localeKeys(locale)
    for (const [key, kind] of expected) {
      if (!actual.has(key)) throw new Error(`${locale} 缺少 ${key}`)
      if (actual.get(key) !== kind) throw new Error(`${locale} 的 ${key} 应为 ${kind}`)
    }
    for (const key of actual.keys()) {
      if (!expected.has(key)) throw new Error(`${locale} 多出 ${key}`)
    }
  }
  generateLocaleSchema()
}
