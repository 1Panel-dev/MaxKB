import Clipboard from 'vue-clipboard3'
import { MsgSuccess, MsgError } from '@/utils/message'
import { t } from '@/locales'
/*
  复制粘贴
*/
export async function copyClick(info: string) {
  const { toClipboard } = Clipboard()
  try {
    await toClipboard(info)
    MsgSuccess(t('common.copySuccess'))
  } catch (e) {
    console.error(e)
    MsgError(t('common.copyError'))
  }
}
