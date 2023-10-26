import { h } from 'vue'
import { ElMessageBox, ElMessage, ElIcon } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'

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

/**
 * 删除数据集
 * @param 参数 message: {title, decription,type}
 */

export const MsgConfirm = ({ title, decription }: any, options?: any) => {
  const message: any = h('div', { class: 'app-confirm' }, [
    h('h4', { class: 'app-confirm-title flex align-center' }, [
      h(ElIcon, { class: 'icon' }, [h(WarningFilled)]),
      h('span', { class: 'ml-16' }, title)
    ]),
    h('div', { class: 'app-confirm-decription mt-8' }, decription)
  ])

  const defaultOptions: Object = {
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    ...options
  }
  return ElMessageBox({ message, ...defaultOptions })
}
