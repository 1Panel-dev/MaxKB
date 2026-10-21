/** API Key 的到期状态与有效期选项，仅供本功能使用。 */
import type { ApiKeyRecord } from '@/api/types'

export const expirationOptions = [
  { label: '永不过期', value: 'never' },
  { label: '7 天有效', value: '7' },
  { label: '30 天有效', value: '30' },
  { label: '90 天有效', value: '90' },
  { label: '180 天有效', value: '180' },
  { label: '自定义', value: 'custom' },
] as const

export type ExpirationType = (typeof expirationOptions)[number]['value']

export function getApiKeyExpiration(record: Pick<ApiKeyRecord, 'is_permanent' | 'expire_time'>, now = Date.now()) {
  if (record.is_permanent) return { label: '永不过期', status: 'normal' } as const
  const timestamp = record.expire_time ? new Date(record.expire_time).getTime() : NaN
  if (!Number.isFinite(timestamp)) return { label: '—', status: 'normal' } as const

  const remaining = timestamp - now
  if (remaining <= 0) return { label: '已过期', status: 'expired' } as const
  if (remaining <= 7 * 86400000) {
    const minutes = Math.ceil(remaining / 60000)
    const label =
      minutes < 60 ? `${minutes}分钟后过期` : minutes < 1440 ? `${Math.ceil(minutes / 60)}小时后过期` : `${Math.ceil(minutes / 1440)}天后过期`
    return { label, status: 'soon' } as const
  }
  return { label: '', status: 'normal' } as const
}

/** 预设有效期从保存时起算；自定义日期保持用户选择。 */
export function getApiKeyExpireTime(type: ExpirationType, customTime: string | null, now = new Date()) {
  if (type === 'never') return null
  if (type === 'custom') return customTime
  const date = new Date(now)
  date.setDate(date.getDate() + Number(type))
  return date.toISOString()
}
