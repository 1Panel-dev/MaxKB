import { get, put } from '../core/request'
import type { LicenseProfile } from '@/api/types'

/** 获取当前平台的授权信息。 */
const getLicense = () => get<LicenseProfile>('/license/profile')

/** 上传并更新平台许可证。 */
const putLicense = (payload: FormData) => put<FormData, LicenseProfile>('/license/profile', payload)

export default { getLicense, putLicense }
