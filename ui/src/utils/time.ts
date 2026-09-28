/** 提供跨页面复用的日期时间计算与格式化函数。 */
type Timestamp = Date | number | string | null | undefined

function getCheckedDate(timestamp: Timestamp) {
  if (!timestamp) return false

  const date = timestamp instanceof Date ? timestamp : new Date(timestamp)
  if (Number.isNaN(date.getTime())) return false

  return date
}

function padTimePart(value: number) {
  return String(value).padStart(2, '0')
}

function formatDateParts(date: Date) {
  const year = date.getFullYear()
  const month = padTimePart(date.getMonth() + 1)
  const day = padTimePart(date.getDate())

  return `${year}-${month}-${day}`
}

/**
 * 获取本地时区中当天之前指定天数的日期。
 * 使用日历日计算以正确处理跨月、跨年和夏令时，无效天数返回空字符串。
 */
export function beforeDay(days: number | string) {
  const normalizedDays = Number(days)
  if (!Number.isFinite(normalizedDays)) return ''

  const date = new Date()
  date.setDate(date.getDate() - normalizedDays)
  return formatDateParts(date)
}

/** 将日期时间格式化为 `YYYY-MM-DD HH:mm:ss`，无效值原样返回。 */
export function datetimeFormat<T extends Timestamp>(timestamp: T): string | T {
  const date = getCheckedDate(timestamp)
  if (!date) return timestamp

  const year = date.getFullYear()
  const month = padTimePart(date.getMonth() + 1)
  const day = padTimePart(date.getDate())
  const hours = padTimePart(date.getHours())
  const minutes = padTimePart(date.getMinutes())
  const seconds = padTimePart(date.getSeconds())

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/** 将日期格式化为 `YYYY-MM-DD`，无效值原样返回。 */
export function dateFormat<T extends Timestamp>(timestamp: T): string | T {
  const date = getCheckedDate(timestamp)
  if (!date) return timestamp

  return formatDateParts(date)
}

/**
 * 格式化相对时间：不足 10 分钟显示“刚刚”，不足 1 小时按 10 分钟向下取整，
 * 不足 24 小时显示整小时，不足 8 天显示整天，其余显示 YYYY-MM-DD。
 * 空值或无效时间返回空字符串，未来时间显示“刚刚”；天数按每 24 小时计算。
 */
export function relativeTimeFormat(timestamp: Timestamp): string {
  const date = getCheckedDate(timestamp)
  if (!date) return ''

  const elapsedMinutes = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000))
  if (elapsedMinutes < 10) return '刚刚'
  if (elapsedMinutes < 60) return `${Math.floor(elapsedMinutes / 10) * 10}分钟前`
  if (elapsedMinutes < 1440) return `${Math.floor(elapsedMinutes / 60)}小时前`
  if (elapsedMinutes < 8 * 1440) return `${Math.floor(elapsedMinutes / 1440)}天前`
  return formatDateParts(date)
}
