/** 提供统一的 Element Plus 全局消息提示。 */

import { ElMessage, ElMessageBox, type ElMessageBoxOptions, type MessageOptions, type MessageType } from 'element-plus'

type MessageContent = MessageOptions['message']
type MessageOverrides = Omit<Partial<MessageOptions>, 'message' | 'type'>
type ConfirmContent = NonNullable<ElMessageBoxOptions['message']>
type ConfirmOverrides = Omit<ElMessageBoxOptions, 'boxType' | 'message' | 'title'>

const DEFAULT_MESSAGE_OPTIONS: MessageOverrides = { duration: 3_000, showClose: true }

function MKMessage(type: MessageType, message: MessageContent, options?: MessageOverrides) {
  return ElMessage({ ...DEFAULT_MESSAGE_OPTIONS, ...options, message, type })
}

/** 显示成功消息。 */
export function MsgSuccess(message: MessageContent, options?: MessageOverrides) {
  return MKMessage('success', message, options)
}

/** 显示普通信息。 */
export function MsgInfo(message: MessageContent, options?: MessageOverrides) {
  return MKMessage('info', message, options)
}

/** 显示警告消息。 */
export function MsgWarning(message: MessageContent, options?: MessageOverrides) {
  return MKMessage('warning', message, options)
}

/** 显示错误消息。 */
export function MsgError(message: MessageContent, options?: MessageOverrides) {
  return MKMessage('error', message, options)
}

/** 显示确认对话框，确认时 resolve，取消或关闭时 reject。 */
export function MsgConfirm(title: string, message?: ConfirmContent, options?: ConfirmOverrides) {
  return ElMessageBox.confirm(message, title, { cancelButtonText: '取消', confirmButtonText: '删除', confirmButtonType: 'danger', showCancelButton: true, ...options })
}
