import { ElMessageBox, ElMessage } from 'element-plus'

export const MsgSuccess = (message: string) => {
  ElMessage.success({
    message: message,
    type: 'success',
    showClose: true,
    duration: 1500
  })
}

export const MsgInfo = (message: string) => {
  ElMessage.info({
    message: message,
    type: 'info',
    showClose: true,
    duration: 1500
  })
}

export const MsgWarning = (message: string) => {
  ElMessage.warning({
    message: message,
    type: 'warning',
    showClose: true,
    duration: 1500
  })
}

export const MsgError = (message: string) => {
  ElMessage.error({
    message: message,
    type: 'error',
    showClose: true,
    duration: 1500
  })
}

export const MsgConfirm = (message: string, options = {}) => {
  const defaultOptions: Object = {
    type: 'warning',
    ...options
  }
  return ElMessageBox.confirm(message, '确认', defaultOptions)
}
