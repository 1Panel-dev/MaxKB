/** API Key 的到期状态与有效期选项，仅供本功能使用。 */
import { computed, reactive } from 'vue'
import type { ApiKeyRecord } from '@/api/types'
import { t } from '@/locales'

export const expirationOptions = reactive([
  { label: computed(() => t('apiKey.expiration.never')), value: 'never' },
  { label: computed(() => t('apiKey.expiration.validDays', { count: 7 })), value: '7' },
  { label: computed(() => t('apiKey.expiration.validDays', { count: 30 })), value: '30' },
  { label: computed(() => t('apiKey.expiration.validDays', { count: 90 })), value: '90' },
  { label: computed(() => t('apiKey.expiration.validDays', { count: 180 })), value: '180' },
  { label: computed(() => t('common.options.custom')), value: 'custom' },
] as const)

export type ExpirationType = (typeof expirationOptions)[number]['value']

export function getApiKeyExpiration(record: Pick<ApiKeyRecord, 'is_permanent' | 'expire_time'>, now = Date.now()) {
  if (record.is_permanent) return { label: t('apiKey.expiration.never'), status: 'normal' } as const
  const timestamp = record.expire_time ? new Date(record.expire_time).getTime() : NaN
  if (!Number.isFinite(timestamp)) return { label: '—', status: 'normal' } as const

  const remaining = timestamp - now
  if (remaining <= 0) return { label: t('apiKey.expiration.expired'), status: 'expired' } as const
  if (remaining <= 7 * 86400000) {
    const minutes = Math.ceil(remaining / 60000)
    const label =
      minutes < 60
        ? t('apiKey.expiration.minutes', { count: minutes })
        : minutes < 1440
          ? t('apiKey.expiration.hours', { count: Math.ceil(minutes / 60) })
          : t('apiKey.expiration.days', { count: Math.ceil(minutes / 1440) })
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
