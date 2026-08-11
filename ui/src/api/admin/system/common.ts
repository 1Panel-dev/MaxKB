import { get } from '../core/request'

/** 获取默认密码。 */
const getDefaultPassword = () => {
  return get<{ password: string }>(`/user_manage/password`)
}

export default {
  getDefaultPassword,
}
