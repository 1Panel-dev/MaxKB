export const FOLDER_SORT = {
  CREATE_TIME_ASC: 'create_time_asc',
  CREATE_TIME_DESC: 'create_time_desc',
  NAME_ASC: 'name_asc',
  NAME_DESC: 'name_desc',
  CUSTOM: 'custom',
} as const

export type FolderSort = (typeof FOLDER_SORT)[keyof typeof FOLDER_SORT]
