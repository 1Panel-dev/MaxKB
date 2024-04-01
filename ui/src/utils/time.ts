import moment from 'moment'

// 当天日期 YYYY-MM-DD
export const nowDate = moment().format('YYYY-MM-DD')

// 当前时间的前n天
export function beforeDay(n: number | string) {
  return moment().subtract(n, 'days').format('YYYY-MM-DD')
}

const getCheckDate = (timestamp: any) => {
  if (!timestamp) return false
  const dt = new Date(timestamp)
  if (isNaN(dt.getTime())) return false
  return dt
}
export const datetimeFormat = (timestamp: any) => {
  const dt = getCheckDate(timestamp)
  if (!dt) return timestamp

  const y = dt.getFullYear()
  const m = (dt.getMonth() + 1 + '').padStart(2, '0')
  const d = (dt.getDate() + '').padStart(2, '0')
  const hh = (dt.getHours() + '').padStart(2, '0')
  const mm = (dt.getMinutes() + '').padStart(2, '0')
  const ss = (dt.getSeconds() + '').padStart(2, '0')

  return `${y}-${m}-${d} ${hh}:${mm}:${ss}`
}

export const dateFormat = (timestamp: any) => {
  const dt = getCheckDate(timestamp)
  if (!dt) return timestamp

  const y = dt.getFullYear()
  const m = (dt.getMonth() + 1 + '').padStart(2, '0')
  const d = (dt.getDate() + '').padStart(2, '0')

  return `${y}-${m}-${d}`
}
