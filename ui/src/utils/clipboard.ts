import Clipboard from 'vue-clipboard3'
import { MsgSuccess, MsgError } from '@/utils/message'
/*
  复制粘贴
*/
export async function copyClick(info: string) {
  const { toClipboard } = Clipboard()
  try {
    await toClipboard(info)
    MsgSuccess('复制成功')
  } catch (e) {
    console.error(e)
    MsgError('复制失败')
  }
}
