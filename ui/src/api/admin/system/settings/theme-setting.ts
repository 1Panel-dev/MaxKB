import { get, put } from '../../core/request'

/** 保存系统外观主题设置。 */
const putThemeSetting = (payload: FormData) => {
  return put<FormData, boolean>('/display/update', payload)
}

export default { putThemeSetting }
