import type { CascaderOption } from 'element-plus'
import { SCHEDULE_TYPE } from '@/api/enums'

const scheduleTimes = Array.from({ length: 24 }, (_, hour) => {
  const time = `${String(hour).padStart(2, '0')}:00`
  return { label: time, value: time }
})
/** 触发器、长期记忆与知识库定时同步共用的周期级联选项；使用方只读。 */
export const SCHEDULE_OPTION: CascaderOption[] = [
  { label: '每日', value: SCHEDULE_TYPE.DAILY, children: scheduleTimes },
  {
    label: '每周',
    value: SCHEDULE_TYPE.WEEKLY,
    children: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'].map((label, index) => ({ label, value: index + 1, children: scheduleTimes })),
  },
  {
    label: '每月',
    value: SCHEDULE_TYPE.MONTHLY,
    children: Array.from({ length: 31 }, (_, index) => ({ label: `${index + 1} 日`, value: String(index + 1), children: scheduleTimes })),
  },
  {
    label: '按间隔',
    value: SCHEDULE_TYPE.INTERVAL,
    children: [
      {
        label: '小时',
        value: 'hours',
        children: Array.from({ length: 24 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
      {
        label: '分钟',
        value: 'minutes',
        children: Array.from({ length: 60 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
    ],
  },
]
