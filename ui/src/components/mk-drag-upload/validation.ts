import type { DragUploadFile } from './types'

/** 文件校验只返回文案，由页面或表单统一使用 MsgWarning 提示。 */
export function getUploadValidationMessage(files: DragUploadFile[], required = true): string | undefined {
  if (files.some((file) => file.status === 'ready' || file.status === 'uploading')) {
    return '文件正在上传，请稍候'
  }
  if (!required && !files.length) return
  if (!files.some((file) => file.status === 'success')) {
    return '没有上传成功的文件，请重新上传'
  }
}
