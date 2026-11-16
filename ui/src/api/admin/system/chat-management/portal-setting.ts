import type { PortalSetting, PortalSettingPayload } from '@/api/types'
import { get, put } from '../../core/request'

/** 获取门户基本信息与访问配置。 */
const getPortalSetting = () => get<PortalSetting>('/portal')

/** 保存门户基本信息或访问配置。 */
const putPortalSetting = (payload: PortalSettingPayload | FormData) => put<PortalSettingPayload | FormData, PortalSetting>('/portal', payload)

export default { getPortalSetting, putPortalSetting }
