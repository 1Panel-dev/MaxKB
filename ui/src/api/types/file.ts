import type { FILE_SOURCE_TYPE } from '@/api/enums'

export type FileSourceType = (typeof FILE_SOURCE_TYPE)[keyof typeof FILE_SOURCE_TYPE]

/** 服务端读取远程 URL 后返回的内容与响应头。 */
export interface UrlFileContent {
  status_code: number
  'Content-Type': string
  'Content-Length': string | number | null
  content: string
}
