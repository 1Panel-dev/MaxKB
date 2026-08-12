import { get, post, put } from '../core/request'
import type { QrLoginPlatform, QrLoginPlatformRequest } from '@/api/types'

const prefix = '/chat_user/auth/platform/source'

/** 获取对话用户扫码登录平台配置。 */
const getQrLoginPlatforms = () => {
  return get<QrLoginPlatform[]>(prefix)
}

/** 保存对话用户扫码登录平台配置。 */
const postQrLoginPlatform = (platform: QrLoginPlatformRequest) => {
  return post<QrLoginPlatformRequest, boolean>(prefix, platform)
}

/** 校验对话用户扫码登录平台配置是否可用。 */
const putValidateQrLoginPlatform = (platform: QrLoginPlatformRequest) => {
  return put<QrLoginPlatformRequest, boolean>(prefix, platform)
}

export default {
  getQrLoginPlatforms,
  postQrLoginPlatform,
  putValidateQrLoginPlatform,
}
