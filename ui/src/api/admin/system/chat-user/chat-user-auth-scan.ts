import { get, post, put } from '../../core/request'
import type { QrLoginPlatform, QrLoginPlatformPayload } from '@/api/types'

const prefix = '/chat_user/auth/platform/source'

/** 获取对话用户扫码登录平台配置。 */
const getQrLoginPlatforms = () => {
  return get<QrLoginPlatform[]>(prefix)
}

/** 保存对话用户扫码登录平台配置。 */
const postQrLoginPlatform = (payload: QrLoginPlatformPayload) => {
  return post<QrLoginPlatformPayload, boolean>(prefix, payload)
}

/** 校验对话用户扫码登录平台配置是否可用。 */
const putValidateQrLoginPlatform = (payload: QrLoginPlatformPayload) => {
  return put<QrLoginPlatformPayload, boolean>(prefix, payload)
}

export default {
  getQrLoginPlatforms,
  postQrLoginPlatform,
  putValidateQrLoginPlatform,
}
