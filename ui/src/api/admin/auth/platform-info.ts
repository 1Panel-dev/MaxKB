/** 提供 Admin 登录前所需的平台公开信息接口。 */

import { get } from '../core/request'
import type { LoginConfig, PlatformInfo, ThemeInfo } from './types'

/** 获取平台版本、许可信息及登录加密公钥。 */
export function getPlatformInfo() {
  return get<PlatformInfo>('/profile')
}

/** 获取当前版本启用的登录方式。 */
export function getLoginConfig() {
  return get<LoginConfig>('/login/auth/setting')
}

/** 获取当前外观主题信息。 */
export function getThemeInfo() {
  return get<ThemeInfo>('/display/info')
}

export default {
  getLoginConfig,
  getPlatformInfo,
  getThemeInfo,
}
