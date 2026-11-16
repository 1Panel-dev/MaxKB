import type { FileSourceType, UrlFileContent } from '@/api/types'
import type { AxiosProgressEvent } from 'axios'
import { del, get, postUpload } from './core/request'

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

/** 删除已上传的资源文件。 */
const deleteFile = (fileId: string) => del(`/oss/file/${fileId}`)

/** 获取 URL 文件内容、类型和大小。 */
const getUrlFile = (applicationId: string, url: string) => get<UrlFileContent>(`/oss/get_url/${applicationId}`, { url })

export default { getUrlFile, postUploadFile, deleteFile }
