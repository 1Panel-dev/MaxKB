import { get, post, put } from '../core/request'
import type { QrLoginPlatform, QrLoginPlatformRequest } from '@/api/types'

const prefix = '/platform'

/** 获取扫码登录平台配置。 */
const getQrLoginPlatforms = () => {
  return get<QrLoginPlatform[]>(prefix)
}

/** 校验扫码登录平台配置是否可用。 */
const postQrLoginPlatformConnection = (platform: QrLoginPlatformRequest) => {
  return post<QrLoginPlatformRequest, boolean>(`${prefix}/connection`, platform)
}

/** 保存扫码登录平台配置。 */
const putQrLoginPlatform = (platform: QrLoginPlatformRequest) => {
  return put<QrLoginPlatformRequest, boolean>(prefix, platform)
}

export default {
  getQrLoginPlatforms,
  postQrLoginPlatformConnection,
  putQrLoginPlatform,
}
