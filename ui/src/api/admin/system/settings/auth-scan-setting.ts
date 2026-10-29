import { get, post, put } from '../../core/request'
import type { QrLoginPlatform, QrLoginPlatformPayload } from '@/api/types'

const prefix = '/platform/source'

/** 获取扫码登录平台配置。 */
const getQrLoginPlatforms = () => {
  return get<QrLoginPlatform[]>(prefix)
}

/** 保存扫码登录平台配置。 */
const saveQrLoginPlatform = (payload: QrLoginPlatformPayload) => {
  return post<QrLoginPlatformPayload, boolean>(prefix, payload)
}

/** 校验扫码登录平台配置是否可用。 */
const validateQrLoginPlatform = (payload: QrLoginPlatformPayload) => {
  return put<QrLoginPlatformPayload, boolean>(prefix, payload)
}

export default { getQrLoginPlatforms, validateQrLoginPlatform, saveQrLoginPlatform }
