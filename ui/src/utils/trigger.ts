import { t } from '@/locales'
import { relatedObject } from '@/utils/array'

const times = Array.from({ length: 24 }, (_, i) => {
  const time = i.toString().padStart(2, '0') + ':00'
  return { label: time, value: time }
})
const days = Array.from({ length: 31 }, (_, i) => {
  i = i + 1
  const day = i.toString() + t('views.trigger.triggerCycle.days')
  return { label: day, value: i.toString(), children: times }
})
const hours = Array.from({ length: 24 }, (_, i) => {
  i = i + 1
  const time = i.toString().padStart(2, '0')
  return { label: time, value: i }
})
const minutes = Array.from({ length: 60 }, (_, i) => {
  i = i + 1
  const time = i.toString().padStart(2, '0')
  return { label: time, value: i }
})
export const triggerCycleOptions = [
  {
    value: 'daily',
    label: t('views.trigger.triggerCycle.daily'),
    multiple: true,
    children: times,
  },
  {
    value: 'weekly',
    label: t('views.trigger.triggerCycle.weekly'),
    children: [
      { label: t('views.trigger.triggerCycle.sunday'), value: 7, children: times },
      { label: t('views.trigger.triggerCycle.monday'), value: 1, children: times },
      { label: t('views.trigger.triggerCycle.tuesday'), value: 2, children: times },
      { label: t('views.trigger.triggerCycle.wednesday'), value: 3, children: times },
      { label: t('views.trigger.triggerCycle.thursday'), value: 4, children: times },
      { label: t('views.trigger.triggerCycle.friday'), value: 5, children: times },
      { label: t('views.trigger.triggerCycle.saturday'), value: 6, children: times },
    ],
  },
  { value: 'monthly', label: t('views.trigger.triggerCycle.monthly'), children: days },
  {
    value: 'interval',
    label: t('views.trigger.triggerCycle.interval'),
    children: [
      { label: t('views.trigger.triggerCycle.hours'), value: 'hours', children: hours },
      { label: t('views.trigger.triggerCycle.minutes'), value: 'minutes', children: minutes },
    ],
  },
]

export function getTriggerCycleLabel(data: any) {
  const { schedule_type, days, time, interval_unit, interval_value } = data
  if (!schedule_type) return ''
  const scheduleOption = triggerCycleOptions.find((option) => option.value === schedule_type)
  if (!scheduleOption) return ''
  const baseLabel = scheduleOption.label
  switch (schedule_type) {
    case 'daily':
      if (time) {
        const timeLabel = relatedObject(scheduleOption.children, time.toString(), 'value')?.label
        return `${baseLabel}/${timeLabel}`
      }
      return baseLabel

    case 'weekly':
      if (days && time) {
        const dayOption:any = scheduleOption.children.find(
          (day) => day.value.toString() === days.toString(),
        )
        if (dayOption) {
          const timeLabel = relatedObject(dayOption.children, time.toString(), 'value')?.label
          return `${baseLabel}/${dayOption.label}/${timeLabel}`
        }
      }
      return baseLabel

    case 'monthly':
      if (days && time) {
        const dayOption:any = scheduleOption.children.find(
          (day) => day.value.toString() === days.toString(),
        )
        if (dayOption) {
          const timeLabel = relatedObject(dayOption.children, time.toString(), 'value')?.label
          return `${baseLabel}/${dayOption.label}/${timeLabel}`
        }
      }
      return baseLabel

    case 'interval':
      if (interval_unit) {
        const unitOption:any = scheduleOption.children.find((unit) => unit.value === interval_unit)
        if (unitOption) {
          const intervalLabel = relatedObject(unitOption.children, interval_value, 'value')?.label
          return `${baseLabel}/${unitOption.label}/${intervalLabel}`
        }
      }
      return baseLabel

    default:
      return baseLabel
  }
}
