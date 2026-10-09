import type { UploadRawFile, UploadUserFile } from 'element-plus'

/** 多文件上传的展示状态。 */
export interface DragUploadFile extends UploadUserFile {
  file_id?: string
  errMsg?: string
  canRetry?: boolean
}

/** 由调用方提供具体上传接口，组件管理进度、完成状态和取消。 */
export type DragUploadHandler = (file: UploadRawFile, onProgress: (percent: number) => void) => { request: Promise<string>; abort: () => void }
