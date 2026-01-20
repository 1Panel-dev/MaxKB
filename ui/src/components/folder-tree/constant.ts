import { t } from '@/locales'

export const SORT_TYPES = {
  CREATE_TIME_ASC: 'createTime-asc',
  CREATE_TIME_DESC: 'createTime-desc',
  NAME_ASC: 'name-asc',
  NAME_DESC: 'name-desc',
  CUSTOM: 'custom',
} as const

export type SortType = (typeof SORT_TYPES)[keyof typeof SORT_TYPES]

export const SORT_MENU_CONFIG = [
  {
    title: 'time',
    items: [
      { label: t('components.folder.ascTime'), value: SORT_TYPES.CREATE_TIME_ASC },
      { label: t('components.folder.descTime'), value: SORT_TYPES.CREATE_TIME_DESC },
    ],
  },
  {
    title: 'name',
    items: [
      { label: t('components.folder.ascName'), value: SORT_TYPES.NAME_ASC },
      { label: t('components.folder.descName'), value: SORT_TYPES.NAME_DESC },
    ],
  },
  {
    items: [{ label: t('components.folder.custom'), value: SORT_TYPES.CUSTOM }],
  },
]
