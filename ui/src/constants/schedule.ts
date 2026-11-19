import { computed, reactive } from 'vue'
import type { CascaderOption } from 'element-plus'
import { SCHEDULE_TYPE } from '@/api/enums'
import { t } from '@/locales'

const scheduleTimes = Array.from({ length: 24 }, (_, hour) => {
  const time = `${String(hour).padStart(2, '0')}:00`
  return { label: time, value: time }
})
/** 触发器、长期记忆与知识库定时同步共用的周期级联选项；使用方只读。 */
export const SCHEDULE_OPTION: CascaderOption[] = reactive([
  { label: computed(() => t('common.schedule.daily')), value: SCHEDULE_TYPE.DAILY, children: scheduleTimes },
  {
    label: computed(() => t('common.schedule.weekly')),
    value: SCHEDULE_TYPE.WEEKLY,
    children: [
      { label: computed(() => t('common.schedule.weekdays.monday')) },
      { label: computed(() => t('common.schedule.weekdays.tuesday')) },
      { label: computed(() => t('common.schedule.weekdays.wednesday')) },
      { label: computed(() => t('common.schedule.weekdays.thursday')) },
      { label: computed(() => t('common.schedule.weekdays.friday')) },
      { label: computed(() => t('common.schedule.weekdays.saturday')) },
      { label: computed(() => t('common.schedule.weekdays.sunday')) },
    ].map((weekday, index) => ({ ...weekday, value: index + 1, children: scheduleTimes })),
  },
  {
    label: computed(() => t('common.schedule.monthly')),
    value: SCHEDULE_TYPE.MONTHLY,
    children: Array.from({ length: 31 }, (_, index) => ({
      label: computed(() => `${index + 1} ${t('common.schedule.day')}`),
      value: String(index + 1),
      children: scheduleTimes,
    })),
  },
  {
    label: computed(() => t('common.schedule.interval')),
    value: SCHEDULE_TYPE.INTERVAL,
    children: [
      {
        label: computed(() => t('common.schedule.units.hours')),
        value: 'hours',
        children: Array.from({ length: 24 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
      {
        label: computed(() => t('common.schedule.units.minutes')),
        value: 'minutes',
        children: Array.from({ length: 60 }, (_, index) => ({ label: String(index + 1).padStart(2, '0'), value: index + 1 })),
      },
    ],
  },
])
