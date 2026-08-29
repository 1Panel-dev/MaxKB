import { get, put } from '../../core/request'
import type { ThemeInfo } from '../../auth/types'

/** 保存系统外观主题设置。 */
const putThemeSetting = (payload: FormData) => {
  return put<FormData, boolean>('/settings/theme', payload)
}

export default {
  putThemeSetting,
}
