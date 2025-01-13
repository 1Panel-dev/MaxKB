import { ElMessageBox, ElMessage } from 'element-plus'
import { t } from '@/locales'

export const MsgSuccess = (message: string) => {
  ElMessage.success({
    message: message,
    type: 'success',
    showClose: true,
    duration: 3000
  })
}

export const MsgInfo = (message: string) => {
  ElMessage.info({
    message: message,
    type: 'info',
    showClose: true,
    duration: 3000
  })
}

export const MsgWarning = (message: string) => {
  ElMessage.warning({
    message: message,
    type: 'warning',
    showClose: true,
    duration: 3000
  })
}

export const MsgError = (message: string) => {
  ElMessage.error({
    message: message,
    type: 'error',
    showClose: true,
    duration: 3000
  })
}

export const MsgAlert = (title: string, description: string, options?: any) => {
  const defaultOptions: Object = {
    confirmButtonText: t('common.confirm'),
    ...options
  }
  return ElMessageBox.alert(description, title, defaultOptions)
}

/**
 * 删除知识库
 * @param 参数 message: {title, description,type}
 */

export const MsgConfirm = (title: string, description: string, options?: any) => {
  const defaultOptions: Object = {
    showCancelButton: true,
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    ...options
  }
  return ElMessageBox.confirm(description, title, defaultOptions)
}
