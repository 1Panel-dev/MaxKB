import type { AxiosProgressEvent } from 'axios'
import { postUpload } from './core/request'
import type { FileSourceType } from '@/api/types'

/** 上传资源文件，支持可选的进度回调与取消操作。 */
const postUploadFile = (
  file: File,
  sourceId: string | undefined,
  sourceType: FileSourceType,
  onProgress?: (percent: number, event: AxiosProgressEvent) => void,
) => {
  const formData = new FormData()
  formData.append('file', file)
  if (sourceId !== undefined) formData.append('source_id', sourceId)
  formData.append('source_type', sourceType)
  return postUpload<string>('/oss/file', formData, onProgress)
}

export default { postUploadFile }
