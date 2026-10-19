/**
 * 工具执行结果：工具返回哪一种结果，决定 agent 循环接下来怎么走。
 * 工具层（agent 继续循环）：
 * - SuccessResult：工具成功，内容回喂模型，循环继续；
 * - ErrorResult：工具失败，错误回喂模型让其自行修正，循环继续，工具卡标为失败。
 * agent 层（立即结束所在 agent）：
 * - AgentSuccessResult：agent 成功结束（status=done），data 作为该 agent 的交付上抛给调用方（如父 agent 的委派工具）；
 * - AgentErrorResult：agent 失败结束（status=error），message 作为失败原因上抛，不再让模型续修，工具卡标为失败。
 * 工具直接返回普通值时按 SuccessResult 处理；抛出的异常按 ErrorResult 处理。
 */
export abstract class ToolResult {
  /** 回喂给模型的内容 */
  abstract toContent(): unknown
}

export class SuccessResult<T = unknown> extends ToolResult {
  constructor(readonly data?: T) {
    super()
  }

  toContent() {
    return this.data ?? { ok: true }
  }
}

export class ErrorResult extends ToolResult {
  constructor(
    readonly message: string,
    /** 结构化的错误细节（如校验失败的字段列表），可选 */
    readonly detail?: unknown,
  ) {
    super()
  }

  toContent() {
    return this.detail === undefined ? { error: this.message } : { error: this.message, detail: this.detail }
  }
}

export class AgentSuccessResult<T = unknown> extends ToolResult {
  constructor(readonly data?: T) {
    super()
  }

  toContent() {
    return this.data ?? { ok: true }
  }
}

export class AgentErrorResult extends ToolResult {
  constructor(
    readonly message: string,
    /** 结构化的错误细节，可选 */
    readonly detail?: unknown,
  ) {
    super()
  }

  toContent() {
    return this.detail === undefined ? { error: this.message } : { error: this.message, detail: this.detail }
  }
}

/** 把工具返回值统一成 ToolResult：普通值视为成功 */
export function toToolResult(value: unknown): ToolResult {
  return value instanceof ToolResult ? value : new SuccessResult(value)
}

/** 工具卡是否标为成功：两种失败结果都标为失败 */
export function isFailureResult(result: ToolResult): boolean {
  return result instanceof ErrorResult || result instanceof AgentErrorResult
}
