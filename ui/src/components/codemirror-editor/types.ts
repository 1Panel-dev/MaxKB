/** CodeMirror 异步语法检查使用的行列诊断信息。 */
export interface CodeLintIssue {
  column: number
  endColumn?: number
  endLine?: number
  line: number
  message: string
  type: 'error' | 'warning'
}
