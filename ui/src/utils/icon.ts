/** 提供跨页面复用的文件后缀识别、类型校验和图标匹配函数。 */

import type { KnowledgeType } from '@/api/types'
import { KNOWLEDGE_TYPE_KEY, KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import fileImageIcon from '@/assets/file-type/file-image-icon.svg'
import webLinkIcon from '@/assets/file-type/web-link-icon.svg'
import { IMAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS } from '@/constants/file-type'

/** 获取文件名中不含点号的大写后缀；无有效后缀时返回空字符串。 */
export function getFileExtension(fileName: string): string {
  const baseName = fileName.split(/[\\/]/).pop() ?? ''
  const separatorIndex = baseName.lastIndexOf('.')

  if (separatorIndex <= 0 || separatorIndex === baseName.length - 1) return ''
  return baseName.slice(separatorIndex + 1).toUpperCase()
}

/** 判断文件是否为图片。 */
export function isImage(fileName: string): boolean {
  return IMAGE_EXTENSIONS.includes(getFileExtension(fileName))
}

/** 判断文件是否为文档。 */
export function isDocument(fileName: string): boolean {
  return DOCUMENT_EXTENSIONS.includes(getFileExtension(fileName))
}

/** 判断文件是否为音频。 */
export function isAudio(fileName: string): boolean {
  return AUDIO_EXTENSIONS.includes(getFileExtension(fileName))
}

/** 判断文件是否为视频。 */
export function isVideo(fileName: string): boolean {
  return VIDEO_EXTENSIONS.includes(getFileExtension(fileName))
}

/** 返回文件图标 URL；图片标记优先于 Web 知识库类型，未传时按后缀匹配。 */
export function getFileIconUrl(fileName: string, knowledgeType?: KnowledgeType | null, isImageType?: boolean): string {
  if (isImageType) return fileImageIcon
  if (knowledgeType != null && KNOWLEDGE_TYPE_MAP[knowledgeType] === KNOWLEDGE_TYPE_KEY.WEB) return webLinkIcon

  const extension = getFileExtension(fileName)
  let iconName = 'unknown'

  if (isDocument(fileName) || extension === 'DOC' || extension === 'ZIP') {
    // 保留历史文件图标支持，不扩展消息附件的文档类型白名单。
    iconName = extension.toLowerCase()
  } else if (isAudio(fileName)) {
    iconName = 'file-audio'
  } else if (isVideo(fileName)) {
    iconName = 'file-video'
  }

  return new URL(`../assets/file-type/${iconName}-icon.svg`, import.meta.url).href
}

/*
  icon url
*/
export const resetUrl = (url?: string | null, useDefault?: boolean) => {
  const sourceUrl = url || (useDefault ? './favicon.ico' : '')
  if (sourceUrl && sourceUrl.startsWith('./')) {
    return `${window.MaxKB?.prefix}/${sourceUrl.substring(2)}`
  }
  return sourceUrl
}
