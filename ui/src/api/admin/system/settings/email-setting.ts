import { get, post, put } from '../../core/request'
import type { EmailSettingPayload } from '@/api/types'

const prefix = '/email_setting'

/** 获取邮箱设置。 */
const getEmailSetting = () => {
  return get<Partial<EmailSettingPayload>>(prefix)
}

/** 测试邮箱设置是否可用。 */
const postEmailSettingTest = (payload: EmailSettingPayload) => {
  return post<EmailSettingPayload, boolean>(prefix, payload)
}

/** 保存邮箱设置。 */
const putEmailSetting = (payload: EmailSettingPayload) => {
  return put<EmailSettingPayload, boolean>(prefix, payload)
}

export default {
  getEmailSetting,
  postEmailSettingTest,
  putEmailSetting,
}
