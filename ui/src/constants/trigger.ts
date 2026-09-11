import type { CascaderOption } from 'element-plus'
import { TRIGGER_SCHEDULE_TYPE as SCHEDULE, TRIGGER_INTERVAL_UNIT as INTERVAL } from '@/api/enums'

const scheduleTimes = Array.from({ length: 24 }, (_, hour) => {
  const time = `${String(hour).padStart(2, '0')}:00`
  return { label: time, value: time }
})
/** 触发器与长期记忆共用的周期级联选项；使用方只读。 */
export const TRIGGER_SCHEDULE_OPTIONS: CascaderOption[] = [
  { label: '每日', value: SCHEDULE.DAILY, children: scheduleTimes },
  {
    label: '每周',
    value: SCHEDULE.WEEKLY,
    children: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'].map((label, index) => ({ label, value: index + 1, children: scheduleTimes })),
  },
  {
    label: '每月',
    value: SCHEDULE.MONTHLY,
    children: Array.from({ length: 31 }, (_, index) => ({ label: `${index + 1} 日`, value: String(index + 1), children: scheduleTimes })),
  },
  {
    label: '按间隔',
    value: SCHEDULE.INTERVAL,
    children: [
      {
        label: '小时',
        value: INTERVAL.HOURS,
        children: Array.from({ length: 24 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
      {
        label: '分钟',
        value: INTERVAL.MINUTES,
        children: Array.from({ length: 60 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
    ],
  },
]
