/** 提供跨页面复用的文件后缀识别、类型校验和图标匹配函数。 */

const FILE_TYPE_GROUPS = {
  txt: ['txt', 'pdf', 'doc', 'docx', 'md', 'html', 'zip', 'xlsx', 'xls', 'csv'],
  table: ['xlsx', 'xls', 'csv'],
  QA: ['xlsx', 'csv', 'xls', 'zip'],
} as const

const FILE_ICON_EXTENSIONS = new Set<string>(FILE_TYPE_GROUPS.txt)

export type FileTypeGroup = keyof typeof FILE_TYPE_GROUPS

/** 获取文件名中不含点号的小写后缀；无有效后缀时返回空字符串。 */
export function getFileExtension(fileName: string): string {
  const baseName = fileName.split(/[\\/]/).pop() ?? ''
  const separatorIndex = baseName.lastIndexOf('.')

  if (separatorIndex <= 0 || separatorIndex === baseName.length - 1) return ''
  return baseName.slice(separatorIndex + 1).toLowerCase()
}

/** 根据文件后缀返回对应图标 URL，不支持的后缀使用 unknown 图标。 */
export function getFileIconUrl(fileName: string): string {
  const extension = getFileExtension(fileName)
  const iconName = FILE_ICON_EXTENSIONS.has(extension) ? extension : 'unknown'

  return new URL(`../assets/file-type/${iconName}-icon.svg`, import.meta.url).href
}

/** 判断文件后缀是否属于指定的文件类型白名单。 */
export function isAllowedFileType(fileName: string, group: FileTypeGroup): boolean {
  const fileExtension = getFileExtension(fileName)
  return FILE_TYPE_GROUPS[group].some((extension) => extension === fileExtension)
}

/*
  icon url
*/
export const resetUrl = (url?: string | null, useDefault?: boolean) => {
  const sourceUrl = url || (useDefault ? './favicon.ico' : '')
  if (sourceUrl && sourceUrl.startsWith('./')) {
    return `${window.MaxKB?.prefix}/${sourceUrl.substring(2)}`
  }
  return sourceUrl
}


