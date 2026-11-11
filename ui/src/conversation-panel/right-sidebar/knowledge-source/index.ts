import { computed, ref } from 'vue'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import type { ChatParagraphSource, ChatParagraphSourceMeta, DocumentResourceType, KnowledgeType } from '@/api/types'
import { downloadByURL, getFileUrl } from '@/utils/common'
import { MsgInfo } from '@/utils/message'
import { isPdfDocument, type PreviewDocument } from './document-preview/index'

/**
 * 来源文档的打开方式：知识库文件中的 PDF 在知识来源内用 pdf.js 预览，其他文件直接下载，均不交给浏览器原生打开；
 * 网页来源在新窗口打开原网址；无可用地址时提示原因。
 */
export const SOURCE_DOCUMENT_ACTION = {
  PREVIEW: 'PREVIEW',
  DOWNLOAD: 'DOWNLOAD',
  LINK: 'LINK',
  UNAVAILABLE: 'UNAVAILABLE',
} as const

export type SourceDocumentAction = (typeof SOURCE_DOCUMENT_ACTION)[keyof typeof SOURCE_DOCUMENT_ACTION]

/** 知识来源面板展示的分段，字段已按展示需要整理。 */
export interface KnowledgeSourceParagraph {
  key: string
  order: number
  title: string
  content: string
  similarity: string
  vectorLabel: string
  imageUrl: string
  documentName: string
  documentResourceType?: DocumentResourceType | null
  documentAction: SourceDocumentAction
  /** 来源文档地址，UNAVAILABLE 时为空字符串 */
  documentUrl: string
  allowDownload: boolean
  knowledgeName: string
  knowledgeType?: KnowledgeType
}

// 历史快照中 meta 可能是 JSON 字符串，解析失败按无元数据处理
function parseMeta(meta: ChatParagraphSource['meta']): ChatParagraphSourceMeta {
  if (!meta) return {}
  if (typeof meta !== 'string') return meta
  try {
    return JSON.parse(meta) as ChatParagraphSourceMeta
  } catch {
    return {}
  }
}

// 图片文档或命中图片资产时展示召回图片；正文已内嵌同一图片时不重复展示
function getImageUrl(paragraph: ChatParagraphSource) {
  const fileId =
    (paragraph.document_resource_type === DOCUMENT_RESOURCE_TYPE.IMAGE ? paragraph.document_image_id : undefined) || paragraph.hit_asset?.file_id
  if (!fileId || paragraph.content?.includes(`/oss/file/${fileId}`)) return ''
  return getFileUrl(fileId)
}

// 网页来源只接受 http(s) 地址，避免 javascript: 等协议
const toSafeWebUrl = (url?: string) => (url && /^https?:\/\//i.test(url.trim()) ? url.trim() : '')

function getDocumentTarget(documentName: string, meta: ChatParagraphSourceMeta): { action: SourceDocumentAction; url: string } {
  const fileUrl = getFileUrl(meta.source_file_id)
  if (fileUrl) return { action: isPdfDocument(documentName) ? SOURCE_DOCUMENT_ACTION.PREVIEW : SOURCE_DOCUMENT_ACTION.DOWNLOAD, url: fileUrl }
  const webUrl = toSafeWebUrl(meta.source_url)
  if (webUrl) return { action: SOURCE_DOCUMENT_ACTION.LINK, url: webUrl }
  return { action: SOURCE_DOCUMENT_ACTION.UNAVAILABLE, url: '' }
}

function toSourceParagraph(paragraph: ChatParagraphSource, index: number): KnowledgeSourceParagraph {
  const meta = parseMeta(paragraph.meta)
  const documentName = paragraph.document_name?.trim() || ''
  const documentTarget = getDocumentTarget(documentName, meta)
  return {
    key: paragraph.id || String(index),
    order: index + 1,
    title: paragraph.title || '-',
    content: paragraph.content || '',
    similarity: paragraph.similarity?.toFixed(3) ?? '',
    vectorLabel: paragraph.document_resource_type === DOCUMENT_RESOURCE_TYPE.IMAGE || paragraph.hit_asset ? '图片向量' : '文本向量',
    imageUrl: getImageUrl(paragraph),
    documentName,
    documentResourceType: paragraph.document_resource_type,
    documentAction: documentTarget.action,
    documentUrl: documentTarget.url,
    allowDownload: meta.allow_download !== false,
    knowledgeName: paragraph.knowledge_name || '-',
    knowledgeType: paragraph.knowledge_type,
  }
}

/**
 * 知识来源面板 store：当前回答引用的分段（按相似度从高到低整理为展示数据）及正在预览的来源文档。
 * 由右侧栏 store 创建并组合，右侧开合与面板切换由右侧栏 store 维护。
 */
export function createKnowledgeSourceStore() {
  const paragraphs = ref<ChatParagraphSource[]>([])
  // 有值时知识来源显示文档预览，否则显示分段列表
  const previewDocument = ref<PreviewDocument | null>(null)

  // 打开新的知识来源时回到分段列表
  const setParagraphs = (sourceList: ChatParagraphSource[]) => {
    paragraphs.value = sourceList
    previewDocument.value = null
  }

  // 返回分段列表
  const closePreview = () => {
    previewDocument.value = null
  }

  const sourceParagraphs = computed(() =>
    [...paragraphs.value].sort((left, right) => (right.similarity || 0) - (left.similarity || 0)).map(toSourceParagraph),
  )
  const count = computed(() => sourceParagraphs.value.length)

  // 按来源文档的打开方式处理点击；无来源地址时按下载权限给出提示
  const openDocument = (paragraph: KnowledgeSourceParagraph) => {
    const { documentAction, documentName, documentUrl } = paragraph
    if (documentAction === SOURCE_DOCUMENT_ACTION.PREVIEW) previewDocument.value = { name: documentName, url: documentUrl }
    else if (documentAction === SOURCE_DOCUMENT_ACTION.DOWNLOAD) downloadByURL(documentUrl, documentName)
    else if (documentAction === SOURCE_DOCUMENT_ACTION.LINK) window.open(documentUrl, '_blank', 'noopener,noreferrer')
    else MsgInfo(paragraph.allowDownload ? '原文档不存在' : '没有下载权限')
  }

  return { paragraphs, previewDocument, sourceParagraphs, count, setParagraphs, openDocument, closePreview }
}

export type KnowledgeSourceStore = ReturnType<typeof createKnowledgeSourceStore>
