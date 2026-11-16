/** 提供 Admin 登录前所需的平台公开信息接口。 */

import type { BaseProfile, ThemeInfo } from './types'
import type { LoginConfig } from '@/api/types'
import { get } from '../core/request'

/** 获取平台版本、许可信息及登录加密公钥。 */
const getBaseProfile = () => {
  return get<BaseProfile>('/profile')
}

/** 获取当前版本启用的登录方式。 */
const getLoginConfig = () => {
  return get<LoginConfig>('/login/auth/setting')
}

/** 获取当前外观主题信息。 */
const getThemeInfo = () => {
  return get<ThemeInfo>('/display/info')
}

export default { getLoginConfig, getBaseProfile, getThemeInfo }
