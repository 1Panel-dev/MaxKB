import type { ChatContent } from '@/api/types'

interface ContentAggregator {
  // 分片提供 id 时，所有聚合器均优先保留该 id，供调用方继续使用稳定消息键。
  (previous: Partial<ChatContent> | undefined, chunk: Partial<ChatContent> & { id: string }): ChatContent & { id: string }
  (previous: Partial<ChatContent> | undefined, chunk: Partial<ChatContent>): ChatContent
}

// 流式分片聚合:按 id+type 把分片累积成一条内容项(TEXT/REASONING/FAILURE/TOOL/FORM/PROGRESS/GROUP)。
// GROUP 为通用分组容器,分片以嵌套 children 携带组内内容,组内同样按 id+type 合并(可再嵌套 GROUP)。
const TEXT = (prev: Partial<ChatContent> = {}, chunk: Partial<ChatContent>) => {
  return {
    type: 'TEXT',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

const REASONING = (prev: Partial<ChatContent> = {}, chunk: Partial<ChatContent>) => {
  return {
    type: 'REASONING',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
    status: chunk.status ?? prev.status,
  }
}

const FAILURE = (prev: Partial<ChatContent> = {}, chunk: Partial<ChatContent>) => {
  return {
    type: 'FAILURE',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

const TOOL = (prev: Partial<ChatContent> = {}, chunk: Partial<ChatContent>) => {
  return {
    type: 'TOOL',
    id: chunk.id ?? prev.id,
    name: chunk.name ?? prev.name,
    arguments: (prev.arguments || '') + (chunk.arguments || ''),
    content: (prev.content || '') + (chunk.content || ''),
    status: chunk.status ?? prev.status,
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

const FORM = (prev: Partial<ChatContent> = {}, chunk: Partial<ChatContent>) => {
  return {
    type: 'FORM',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    form_field_list: chunk.form_field_list ?? prev.form_field_list,
    form_content_format: chunk.form_content_format ?? prev.form_content_format,
    form_data: chunk.form_data ?? prev.form_data,
    is_submit: chunk.is_submit ?? prev.is_submit,
    position: chunk.position ?? prev.position,
    chat_record_id: chunk.chat_record_id ?? prev.chat_record_id,
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

const PROGRESS = (prev: Partial<ChatContent> = {}, chunk: Partial<ChatContent>) => {
  return {
    type: 'PROGRESS',
    id: chunk.id ?? prev.id,
    status: chunk.status ?? prev.status,
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

// 组内子项:按 id+type 合并分片,规则与顶层一致,嵌套 GROUP 由其聚合函数递归处理
const mergeChildren = (children: ChatContent[] = [], chunkChildren: ChatContent[] = []): ChatContent[] => {
  const mergedChildren = [...children]
  chunkChildren.forEach((item) => {
    const aggregator = aggregators[item?.type]
    if (!aggregator) return
    const index = mergedChildren.findIndex((content) => content.id === item.id && content.type === item.type)
    if (index >= 0) mergedChildren[index] = aggregator(mergedChildren[index] ?? {}, item)
    else mergedChildren.push(aggregator({}, item))
  })
  return mergedChildren
}

const GROUP = (prev: Partial<ChatContent> = {}, chunk: Partial<ChatContent>) => {
  return {
    type: 'GROUP',
    id: chunk.id ?? prev.id,
    name: chunk.name ?? prev.name,
    status: chunk.status ?? prev.status,
    children: mergeChildren(prev.children, chunk.children),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

export const aggregators = {
  TEXT,
  REASONING,
  FAILURE,
  TOOL,
  FORM,
  PROGRESS,
  GROUP,
} as Record<string, ContentAggregator>
