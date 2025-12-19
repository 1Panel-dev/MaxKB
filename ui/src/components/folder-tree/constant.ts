import { t } from '@/locales'


export const SORT_TYPES = {
  CREATE_TIME_ASC: 'createTime-asc',
  CREATE_TIME_DESC: 'createTime-desc',
  NAME_ASC: 'name-asc',
  NAME_DESC: 'name-desc',
  CUSTOM: 'custom'
} as const

export type SortType = typeof SORT_TYPES[keyof typeof SORT_TYPES]

export const SORT_MENU_CONFIG = [
  {
    title: 'time', 
    items: [
      { label: t('components.folder.ascTime', '按创建时间升序'), value: SORT_TYPES.CREATE_TIME_ASC},
      { label: t('components.folder.descTime', '按创建时间降序'), value: SORT_TYPES.CREATE_TIME_DESC },
    ]
  },
  {
    title: 'name',
    items: [
      { label: t('components.folder.ascName', '按名称升序'), value: SORT_TYPES.NAME_ASC },
      { label: t('components.folder.descName', '按名称降序'), value: SORT_TYPES.NAME_DESC },
    ]
  },
  {
    items: [
      { label: t('components.folder.custom', '按用户拖拽排序'), value: SORT_TYPES.CUSTOM },
    ]
  }
]