export class Scroll {
  private bottomSuction: boolean
  private isProgrammaticScroll?: boolean
  private element: HTMLElement

  constructor(element: HTMLElement) {
    this.bottomSuction = true
    this.isProgrammaticScroll = false
    this.element = element
    this.initEventListener()
  }

  private initEventListener() {
    this.element.addEventListener('scroll', () => {
      if (this.isProgrammaticScroll) {
        this.isProgrammaticScroll = undefined
      } else {
        if (this.element.scrollHeight - this.element.scrollTop <= this.element.clientHeight + 15) {
          this.bottomSuction = true
          this.isProgrammaticScroll = true
        } else {
          this.isProgrammaticScroll = undefined
          this.bottomSuction = false
        }
      }
    })
  }

  scrollBottom() {
    if (this.bottomSuction) {
      this.element.scrollTop = this.element.scrollHeight
      this.isProgrammaticScroll = true
    }
  }

  forceBottom() {
    this.bottomSuction = true
    this.isProgrammaticScroll = true
    this.element.scrollTop = this.element.scrollHeight
    requestAnimationFrame(() => {
      this.element.scrollTop = this.element.scrollHeight
      this.isProgrammaticScroll = true
    })
  }
}

const TEXT = (prev: any = {}, chunk: any) => {
  return {
    type: 'TEXT',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra
  }
}

const REASONING = (prev: any, chunk: any) => {
  return {
    type: 'REASONING',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra,
    status: chunk.status ?? prev.status
  }
}

const FAILURE = (prev: any, chunk: any) => {
  return {
    type: 'FAILURE',
    id: chunk.id ?? prev.id,
    content: (prev.content || '') + (chunk.content || ''),
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra
  }
}

const TOOL = (prev: any, chunk: any) => {
  return {
    type: 'TOOL',
    id: chunk.id ?? prev.id,
    toolName: chunk.toolName,
    functionArguments: (prev.functionArguments || '') + (chunk.functionArguments || ''),
    content: (prev.content || '') + (chunk.content || ''),
    status: chunk.status ?? prev.status,
    workflowRunId: chunk.workflowRunId ?? prev.workflowRunId,
    extra: chunk.extra ?? prev.extra
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
    extra: chunk.extra ?? prev.extra
  }
}

export const aggregators: Record<string, (prev: any, chunk: any) => any> = {
  TEXT,
  REASONING,
  FAILURE,
  TOOL,
  FORM
}
