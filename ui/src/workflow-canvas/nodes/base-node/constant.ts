import type { FileUploadSetting } from './types'

export const defaultFileUploadSetting: FileUploadSetting = {
  audio: false,
  document: true,
  fileLimit: 50,
  image: false,
  local_upload: true,
  maxFiles: 3,
  other: false,
  otherExtensions: ['PPT', 'DOC'],
  url_upload: false,
  video: false,
}
