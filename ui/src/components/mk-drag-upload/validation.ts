import type { DragUploadFile } from './types'
import { t } from '@/locales'

/** 文件校验只返回文案，由页面或表单统一使用 MsgWarning 提示。 */
export function getUploadValidationMessage(files: DragUploadFile[], required = true): string | undefined {
  if (files.some((file) => file.status === 'ready' || file.status === 'uploading')) {
    return t('upload.uploadInProgressMessage')
  }
  if (!required && !files.length) return
  if (!files.some((file) => file.status === 'success')) {
    return t('upload.noSuccessfulFilesMessage')
  }
}
