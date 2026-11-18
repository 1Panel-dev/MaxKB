import type { CascaderOption } from 'element-plus'
import { SCHEDULE_TYPE } from '@/api/enums'

const scheduleTimes = Array.from({ length: 24 }, (_, hour) => {
  const time = `${String(hour).padStart(2, '0')}:00`
  return { label: time, value: time }
})
/** 触发器、长期记忆与知识库定时同步共用的周期级联选项；使用方只读。 */
export const SCHEDULE_OPTION: CascaderOption[] = [
  { label: '每日', labelKey: 'common.schedule.daily', value: SCHEDULE_TYPE.DAILY, children: scheduleTimes },
  {
    label: '每周',
    labelKey: 'common.schedule.weekly',
    value: SCHEDULE_TYPE.WEEKLY,
    children: [
      { label: '周一', labelKey: 'common.schedule.weekdays.monday' },
      { label: '周二', labelKey: 'common.schedule.weekdays.tuesday' },
      { label: '周三', labelKey: 'common.schedule.weekdays.wednesday' },
      { label: '周四', labelKey: 'common.schedule.weekdays.thursday' },
      { label: '周五', labelKey: 'common.schedule.weekdays.friday' },
      { label: '周六', labelKey: 'common.schedule.weekdays.saturday' },
      { label: '周日', labelKey: 'common.schedule.weekdays.sunday' },
    ].map((weekday, index) => ({ ...weekday, value: index + 1, children: scheduleTimes })),
  },
  {
    label: '每月',
    labelKey: 'common.schedule.monthly',
    value: SCHEDULE_TYPE.MONTHLY,
    children: Array.from({ length: 31 }, (_, index) => ({ label: `${index + 1} 日`, value: String(index + 1), children: scheduleTimes })),
  },
  {
    label: '按间隔',
    labelKey: 'common.schedule.interval',
    value: SCHEDULE_TYPE.INTERVAL,
    children: [
      {
        label: '小时',
        labelKey: 'common.schedule.units.hours',
        value: 'hours',
        children: Array.from({ length: 24 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
      {
        label: '分钟',
        labelKey: 'common.schedule.units.minutes',
        value: 'minutes',
        children: Array.from({ length: 60 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
    ],
  },
]
