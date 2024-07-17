import moment from 'moment'
import 'moment/dist/locale/zh-cn'
moment.locale('zh-cn')

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

export function fromNowDate(time: any) {
  // 拿到当前时间戳和发布时的时间戳，然后得出时间戳差
  const curTime = new Date()
  const futureTime = new Date(time)
  const timeDiff = futureTime.getTime() - curTime.getTime()

  // 单位换算
  const min = 60 * 1000
  const hour = min * 60
  const day = hour * 24
  const week = day * 7

  // 计算发布时间距离当前时间的周、天、时、分
  const exceedWeek = Math.floor(timeDiff / week)
  const exceedDay = Math.floor(timeDiff / day)
  const exceedHour = Math.floor(timeDiff / hour)
  const exceedMin = Math.floor(timeDiff / min)

  // 最后判断时间差到底是属于哪个区间，然后return
  if (exceedWeek > 0) {
    return ''
  } else {
    if (exceedDay < 7 && exceedDay > 0) {
      return exceedDay + '天后'
    } else {
      if (exceedHour < 24 && exceedHour > 0) {
        return exceedHour + '小时后'
      } else {
        if (exceedMin < 0) {
          return '已过期'
        } else {
          return '即将到期'
        }
      }
    }
  }
}
