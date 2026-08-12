import { get, post, put } from '../core/request'
import type { QrLoginPlatform, QrLoginPlatformRequest } from '@/api/types'

const prefix = '/platform/source'

/** 获取扫码登录平台配置。 */
const getQrLoginPlatforms = () => {
  return get<QrLoginPlatform[]>(prefix)
}

/** 保存扫码登录平台配置。 */
const putQrLoginPlatform = (platform: QrLoginPlatformRequest) => {
  return put<QrLoginPlatformRequest, boolean>(prefix, platform)
}

/** 校验扫码登录平台配置是否可用。 */
const postValidateQrLoginPlatform = (platform: QrLoginPlatformRequest) => {
  return post<QrLoginPlatformRequest, boolean>(`${prefix}`, platform)
}

export default {
  getQrLoginPlatforms,
  postValidateQrLoginPlatform,
  putQrLoginPlatform,
}
