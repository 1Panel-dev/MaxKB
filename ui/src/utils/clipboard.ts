/** 提供跨页面复用的剪贴板操作。 */

import { MsgSuccess } from '@/utils/message'

/** 将非空文本写入剪贴板，并在成功后显示提示。 */
export async function copyText(text: string | null | undefined, successMessage = '已复制') {
  if (!text) return

  await navigator.clipboard.writeText(text)
  MsgSuccess(successMessage)
}
