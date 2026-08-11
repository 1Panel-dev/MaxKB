import { get, post, put } from '../core/request'
import type { EmailSetting } from '@/api/types'

const prefix = '/email_setting'

/** 获取邮箱设置。 */
const getEmailSetting = () => {
  return get<Partial<EmailSetting>>(prefix)
}

/** 测试邮箱设置是否可用。 */
const postEmailSettingTest = (setting: EmailSetting) => {
  return post<EmailSetting, boolean>(prefix, setting)
}

/** 保存邮箱设置。 */
const putEmailSetting = (setting: EmailSetting) => {
  return put<EmailSetting, boolean>(prefix, setting)
}

export default {
  getEmailSetting,
  postEmailSettingTest,
  putEmailSetting,
}
