// 流式分片聚合:按 id+type 把分片累积成一条内容项(TEXT/REASONING/FAILURE/TOOL/FORM/PROGRESS)。
const TEXT = (prev: any = {}, chunk: any) => {
  return {
    type: 'TEXT',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

const REASONING = (prev: any, chunk: any) => {
  return {
    type: 'REASONING',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
    status: chunk.status ?? prev.status,
  }
}

const FAILURE = (prev: any, chunk: any) => {
  return {
    type: 'FAILURE',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

const TOOL = (prev: any, chunk: any) => {
  return {
    type: 'TOOL',
    id: chunk.id ?? prev.id,
    name: chunk.name,
    arguments: (prev.arguments || '') + (chunk.arguments || ''),
    content: (prev.content || '') + (chunk.content || ''),
    status: chunk.status ?? prev.status,
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

const FORM = (prev: any, chunk: any) => {
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

const PROGRESS = (prev: any = {}, chunk: any) => {
  return {
    type: 'PROGRESS',
    id: chunk.id ?? prev.id,
    status: chunk.status ?? prev.status,
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
  }
}

export const aggregators: Record<string, (prev: any, chunk: any) => any> = {
  TEXT,
  REASONING,
  FAILURE,
  TOOL,
  FORM,
  PROGRESS,
}
