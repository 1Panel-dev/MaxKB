import type { FILE_SOURCE_TYPE } from '@/api/enums'

export type FileSourceType = (typeof FILE_SOURCE_TYPE)[keyof typeof FILE_SOURCE_TYPE]
