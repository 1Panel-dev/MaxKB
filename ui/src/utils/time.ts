import moment from 'moment'
import 'moment/dist/locale/zh-cn'

moment.locale('zh-cn')
import {t} from '@/locales'

export const expiredTimeList = {
  'never': t('layout.time.neverExpires'),
  '7': '7 ' + t('layout.time.daysValid'),
  '30': '30 ' + t('layout.time.daysValid'),
  '90': '90 ' + t('layout.time.daysValid'),
  '180': '180 ' + t('layout.time.daysValid'),
  'custom': t('common.custom'),
}

// 当天日期 YYYY-MM-DD
export const nowDate = moment().format('YYYY-MM-DD')

// 当前时间的前n天
export function beforeDay(n: number | string) {
  return moment().subtract(n, 'days').format('YYYY-MM-DD')
}

// 当前时间的n天后的时间戳
export function AfterTimestamp(n: number | string) {
  return moment().add(parseInt(n as string), 'days').format('YYYY-MM-DD HH:mm:ss')
}

export function formatEndDate(date: any) {
  return Number(moment(date).endOf('day').format('x'));
} // date的23点59分

export function formatStartDate(date: any) {
  return Number(moment(date).startOf('day').format('x'));
} // date的0点

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

export function fromNowDate(time: any) {
  const curTime = new Date()
  const futureTime = new Date(time)
  const timeDiff = futureTime.getTime() - curTime.getTime()

  // 统一时间单位
  const absTimeDiff = Math.abs(timeDiff)
  const min = 60 * 1000
  const hour = min * 60
  const day = hour * 24

  // 按优先级判断
  if (timeDiff < 0) {
    return t('layout.time.expired') // 已过期
  }

  if (absTimeDiff < hour) {
    const mins = Math.floor(timeDiff / min)
    return mins > 0 ? mins + t('layout.time.minutesLater') : t('layout.time.expiringSoon')
  }

  if (absTimeDiff < day) {
    return Math.floor(timeDiff / hour) + t('layout.time.hoursLater')
  }

  if (absTimeDiff < day * 7) {
    return Math.floor(timeDiff / day) + t('layout.time.daysLater')
  }
  return ''
}
